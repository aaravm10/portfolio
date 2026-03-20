from flask import Blueprint, render_template, request, jsonify
from pathlib import Path
import pandas as pd
import requests

from utils.auth import get_current_user, login_required
from utils.charts import file_mtime, load_master_xlsx
from config import Config

create_bp = Blueprint('create', __name__, url_prefix='/create')

# Define formations and max players per club
FORMATIONS = {
    "4-4-2":   {"GKP": 1, "DEF": 4, "MID": 4, "FWD": 2},
    "4-3-3":   {"GKP": 1, "DEF": 4, "MID": 3, "FWD": 3},
    "3-5-2":   {"GKP": 1, "DEF": 3, "MID": 5, "FWD": 2},
    "3-4-3":   {"GKP": 1, "DEF": 3, "MID": 4, "FWD": 3},
    "4-2-3-1": {"GKP": 1, "DEF": 4, "MID": 5, "FWD": 1},
    "4-5-1":   {"GKP": 1, "DEF": 4, "MID": 5, "FWD": 1},
    "5-3-2":   {"GKP": 1, "DEF": 5, "MID": 3, "FWD": 2},
    "5-4-1":   {"GKP": 1, "DEF": 5, "MID": 4, "FWD": 1},
}


def _master_xlsx_path():
    return Path("data") / f"premier_league_master_{Config.SEASON}.xlsx"

def _load_dataframe():
    xlsx_path = _master_xlsx_path()
    if not xlsx_path.exists():
        return None
    df = load_master_xlsx(str(xlsx_path), file_mtime(xlsx_path)).copy()
    df["player_name"] = df["player_name"].fillna("")
    df["team"] = df["team"].fillna("")
    df["team_short"] = df["team_short"].fillna("")
    df["position"] = df["position"].fillna("")
    return df

# Helper to fetch FPL bootstrap data for player photos and team badges
def _get_photo_map():
    """Fetch FPL bootstrap to build fpl_id -> photo_url and team badge maps."""
    try:
        resp = requests.get(
            "https://fantasy.premierleague.com/api/bootstrap-static/", timeout=15
        )
        resp.raise_for_status()
        data = resp.json()

        teams = {}
        for t in data["teams"]:
            teams[t["id"]] = (
                f"https://resources.premierleague.com/premierleague/badges/t{t['code']}.png"
            )

        photo_map = {}
        team_map = {}
        for p in data["elements"]:
            fpl_id = p["id"]
            photo_id = p["photo"].replace(".jpg", "").replace(".png", "")
            photo_map[fpl_id] = (
                f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{photo_id}.png"
            )
            team_map[fpl_id] = teams.get(p["team"], "")
        return photo_map, team_map
    except Exception:
        return {}, {}


@create_bp.route('/')
@login_required
def index():
    # Render the team creation page with team and formation options
    current_user = get_current_user()
    df = _load_dataframe()

    teams = []
    if df is not None:
        teams = sorted(
            [t for t in df["team"].dropna().unique().tolist() if t != ""]
        )

    return render_template(
        'create.html',
        current_user=current_user,
        teams=teams,
        formations=list(FORMATIONS.keys()),
    )


@create_bp.route('/api/players')
@login_required
def api_players():
    """Return players filtered by position, team, and search query."""
    position = request.args.get('position', '').strip()
    team = request.args.get('team', '').strip()
    search = request.args.get('search', '').strip()

    df = _load_dataframe()
    if df is None:
        return jsonify({'error': 'Data not available. Fetch data from the Dashboard first.'}), 404

    if position:
        df = df[df["position"] == position]
    if team:
        df = df[df["team"] == team]
    if search:
        df = df[df["player_name"].str.contains(search, case=False, na=False)]

    df = df.sort_values("minutes", ascending=False, na_position="last")

    # Build photo/badge maps from FPL API
    photo_map, badge_map = _get_photo_map()

    players = []
    for _, row in df.head(100).iterrows():
        fpl_id = row.get("fpl_id")
        fpl_id_int = int(fpl_id) if pd.notna(fpl_id) else None

        players.append({
            "player_name": row["player_name"],
            "team_short": row["team_short"],
            "team": row["team"],
            "position": row["position"],
            "minutes": int(row["minutes"]) if pd.notna(row.get("minutes")) else 0,
            "goals": int(row["goals"]) if pd.notna(row.get("goals")) else 0,
            "assists": int(row["assists"]) if pd.notna(row.get("assists")) else 0,
            "photo_url": photo_map.get(fpl_id_int, "") if fpl_id_int else "",
            "team_badge": badge_map.get(fpl_id_int, "") if fpl_id_int else "",
        })

    return jsonify({'players': players})
