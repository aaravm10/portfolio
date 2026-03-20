"""
Utility for fetching per-gameweek player history from the FPL API.
Endpoint: https://fantasy.premierleague.com/api/element-summary/{player_id}/
"""

import time
import requests

# Simple in-memory cache: {fpl_id: (timestamp, history_list)}
_HISTORY_CACHE: dict = {}
_CACHE_TTL = 600  # 10 minutes


def fetch_player_history(fpl_id: int) -> list:
    """
    Fetch per-gameweek history for a player from FPL element-summary endpoint.
    Returns a list of dicts, one per gameweek played. Returns [] on failure.
    """
    now = time.time()
    if fpl_id in _HISTORY_CACHE:
        ts, data = _HISTORY_CACHE[fpl_id]
        if now - ts < _CACHE_TTL:
            return data

    try:
        url = f"https://fantasy.premierleague.com/api/element-summary/{fpl_id}/"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        history = r.json().get("history", [])
        _HISTORY_CACHE[fpl_id] = (now, history)
        return history
    except Exception:
        return []


def get_form_stats(history: list, n_gw: int = 5) -> dict:
    """
    Summarise the last n_gw gameweeks for a player.

    Returns:
        {
            'gws': [{'round', 'minutes', 'goals', 'assists', 'points'}],
            'avg_goals': float,
            'avg_assists': float,
            'avg_points': float,
            'avg_minutes': float,
        }
    """
    recent = [gw for gw in history if gw.get("minutes", 0) > 0][-n_gw:]

    gws = [
        {
            "round": gw.get("round"),
            "minutes": gw.get("minutes", 0),
            "goals": gw.get("goals_scored", 0),
            "assists": gw.get("assists", 0),
            "points": gw.get("total_points", 0),
            "clean_sheets": gw.get("clean_sheets", 0),
        }
        for gw in recent
    ]

    if not gws:
        return {"gws": [], "avg_goals": 0, "avg_assists": 0, "avg_points": 0, "avg_minutes": 0}

    return {
        "gws": gws,
        "avg_goals": round(sum(g["goals"] for g in gws) / len(gws), 2),
        "avg_assists": round(sum(g["assists"] for g in gws) / len(gws), 2),
        "avg_points": round(sum(g["points"] for g in gws) / len(gws), 2),
        "avg_minutes": round(sum(g["minutes"] for g in gws) / len(gws), 1),
    }


def get_cumulative_timeline(history: list) -> list:
    """
    Build cumulative season totals per gameweek.

    Returns:
        [{'round', 'cumulative_goals', 'cumulative_assists', 'cumulative_points', 'cumulative_minutes'}]
    """
    played = [gw for gw in history if gw.get("minutes", 0) > 0 or gw.get("total_points", 0) != 0]

    cum_goals = 0
    cum_assists = 0
    cum_points = 0
    cum_minutes = 0

    timeline = []
    for gw in played:
        cum_goals += gw.get("goals_scored", 0)
        cum_assists += gw.get("assists", 0)
        cum_points += gw.get("total_points", 0)
        cum_minutes += gw.get("minutes", 0)
        timeline.append({
            "round": gw.get("round"),
            "cumulative_goals": cum_goals,
            "cumulative_assists": cum_assists,
            "cumulative_points": cum_points,
            "cumulative_minutes": cum_minutes,
        })

    return timeline
