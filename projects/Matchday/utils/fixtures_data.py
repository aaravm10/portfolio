"""
Utility for fetching fixture difficulty ratings (FDR) and making match predictions
using the FPL fixtures API.
"""

import time
import requests
import pandas as pd

_BOOTSTRAP_CACHE = {"ts": 0, "data": None}
_FIXTURES_CACHE = {"ts": 0, "data": None}
_CACHE_TTL = 600  # 10 minutes


def _fetch_bootstrap():
    now = time.time()
    if _BOOTSTRAP_CACHE["data"] and now - _BOOTSTRAP_CACHE["ts"] < _CACHE_TTL:
        return _BOOTSTRAP_CACHE["data"]
    r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/", timeout=30)
    r.raise_for_status()
    _BOOTSTRAP_CACHE["data"] = r.json()
    _BOOTSTRAP_CACHE["ts"] = now
    return _BOOTSTRAP_CACHE["data"]


def _fetch_raw_fixtures():
    now = time.time()
    if _FIXTURES_CACHE["data"] and now - _FIXTURES_CACHE["ts"] < _CACHE_TTL:
        return _FIXTURES_CACHE["data"]
    r = requests.get("https://fantasy.premierleague.com/api/fixtures/", timeout=30)
    r.raise_for_status()
    _FIXTURES_CACHE["data"] = r.json()
    _FIXTURES_CACHE["ts"] = now
    return _FIXTURES_CACHE["data"]


def get_team_id_map() -> dict:
    """
    Returns {team_id: {'name': str, 'short_name': str, 'code': int}} for all 20 teams.
    """
    bootstrap = _fetch_bootstrap()
    return {
        t["id"]: {
            "name": t["name"],
            "short_name": t["short_name"],
            "code": t["code"],
            "badge_url": f"https://resources.premierleague.com/premierleague/badges/t{t['code']}.png",
        }
        for t in bootstrap["teams"]
    }


def get_current_gameweek() -> int:
    """Returns the current or most recently finished gameweek number."""
    bootstrap = _fetch_bootstrap()
    for event in bootstrap["events"]:
        if event.get("is_current"):
            return event["id"]
    for event in reversed(bootstrap["events"]):
        if event.get("finished"):
            return event["id"]
    return 1


def get_fdr_matrix(n_upcoming: int = 10) -> dict:
    """
    Returns upcoming fixture difficulty per team.

    Result: {
        team_id: [
            {'gw': int, 'opponent_id': int, 'opponent_short': str, 'difficulty': int, 'is_home': bool},
            ...
        ]
    }
    """
    fixtures = _fetch_raw_fixtures()
    team_map = get_team_id_map()
    current_gw = get_current_gameweek()

    # Collect upcoming fixtures (not finished, event > 0)
    upcoming = [
        f for f in fixtures
        if not f.get("finished") and f.get("event") and f["event"] >= current_gw
    ]
    upcoming.sort(key=lambda f: f["event"])

    fdr: dict = {tid: [] for tid in team_map}

    for fix in upcoming:
        gw = fix["event"]
        home_id = fix["team_h"]
        away_id = fix["team_a"]
        home_diff = fix.get("team_h_difficulty", 3)
        away_diff = fix.get("team_a_difficulty", 3)

        if home_id in fdr and len(fdr[home_id]) < n_upcoming:
            fdr[home_id].append({
                "gw": gw,
                "opponent_id": away_id,
                "opponent_short": team_map.get(away_id, {}).get("short_name", "?"),
                "difficulty": home_diff,
                "is_home": True,
            })

        if away_id in fdr and len(fdr[away_id]) < n_upcoming:
            fdr[away_id].append({
                "gw": gw,
                "opponent_id": home_id,
                "opponent_short": team_map.get(home_id, {}).get("short_name", "?"),
                "difficulty": away_diff,
                "is_home": False,
            })

    return fdr


def predict_match(team_h_id: int, team_a_id: int, master_df) -> dict:
    """
    Simple xG-based match prediction.

    Uses season xG/game for each team from the master DataFrame.
    Returns:
        {
            'home_team': str,
            'away_team': str,
            'home_expected': float,
            'away_expected': float,
            'prediction': 'home' | 'away' | 'draw',
            'confidence': 'low' | 'medium' | 'high',
        }
    """
    team_map = get_team_id_map()
    home_info = team_map.get(team_h_id, {})
    away_info = team_map.get(team_a_id, {})
    home_name = home_info.get("name", str(team_h_id))
    away_name = away_info.get("name", str(team_a_id))

    if master_df is None or master_df.empty:
        return {"error": "No data available for prediction"}

    df = master_df.copy()

    def team_xg_stats(team_name):
        team_rows = df[df["team"] == team_name]
        if team_rows.empty:
            return 0.0, 0.0
        total_xg = float(team_rows["xG"].sum()) if "xG" in df.columns else 0.0
        if "games" in df.columns:
            raw_games = team_rows["games"].max()
            games = max(int(raw_games) if pd.notna(raw_games) else 1, 1)
        elif "minutes" in df.columns:
            raw_mins = team_rows["minutes"].max()
            games = max(int(raw_mins / 90) if pd.notna(raw_mins) else 1, 1)
        else:
            games = 1
        # goals conceded: use goals_conceded from GK rows
        gk_rows = team_rows[team_rows["position"] == "GKP"]
        total_gc = float(gk_rows["goals_conceded"].sum()) if (not gk_rows.empty and "goals_conceded" in df.columns) else 0.0
        return total_xg / games, total_gc / games

    home_xg_pg, home_gc_pg = team_xg_stats(home_name)
    away_xg_pg, away_gc_pg = team_xg_stats(away_name)

    # Expected goals: average of own attack and opponent defence
    home_expected = round((home_xg_pg + away_gc_pg) / 2, 2)
    away_expected = round((away_xg_pg + home_gc_pg) / 2, 2)

    diff = home_expected - away_expected
    if abs(diff) < 0.15:
        prediction = "draw"
        confidence = "low"
    elif abs(diff) < 0.4:
        prediction = "home" if diff > 0 else "away"
        confidence = "medium"
    else:
        prediction = "home" if diff > 0 else "away"
        confidence = "high"

    return {
        "home_team": home_name,
        "away_team": away_name,
        "home_expected": home_expected,
        "away_expected": away_expected,
        "prediction": prediction,
        "confidence": confidence,
    }
