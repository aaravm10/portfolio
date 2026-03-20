"""
Flask routes for Personal Watchlist feature.
"""

from flask import Blueprint, render_template, request, jsonify, session
from pathlib import Path
import pandas as pd

from utils.auth import get_current_user, login_required
from utils.charts import file_mtime, load_master_xlsx
from models.user import get_watchlist, add_to_watchlist, remove_from_watchlist
from config import Config
from utils.fixtures_data import _fetch_bootstrap

watchlist_bp = Blueprint('watchlist', __name__, url_prefix='/watchlist')

# Load master DataFrame with caching, used for player stats on watchlist page
def _get_master_df():
    xlsx_path = Path("data") / f"premier_league_master_{Config.SEASON}.xlsx"
    if not xlsx_path.exists():
        return None
    return load_master_xlsx(str(xlsx_path), file_mtime(xlsx_path)).copy()

# Helper to convert values to JSON-serializable format, handling NaNs and rounding
def _to_json_value(value):
    if pd.isna(value):
        return 0
    value = float(value)
    return int(value) if value.is_integer() else round(value, 2)


@watchlist_bp.route('/')
@login_required
def watchlist_page():
    current_user = get_current_user()
    user_id = session.get('user_id')
    watchlist = get_watchlist(user_id)

    players = []
    df = _get_master_df()
    if df is not None and watchlist:
        # Build one fpl_id -> photo URL lookup once per request.
        photo_map = {}
        try:
            bootstrap = _fetch_bootstrap()
            for el in bootstrap.get("elements", []):
                photo_file = el["photo"].replace(".jpg", "").replace(".png", "")
                photo_map[int(el["id"])] = (
                    f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{photo_file}.png"
                )
        except Exception:
            photo_map = {}

        df["player_name"] = df["player_name"].fillna("")
        for name in watchlist:
            row_mask = df["player_name"] == name
            if row_mask.any():
                row = df[row_mask].iloc[0]

                # Build photo URL from fpl_id
                fpl_id = row.get("fpl_id")
                photo_url = ""
                if pd.notna(fpl_id):
                    photo_url = photo_map.get(int(fpl_id), "")

                players.append({
                    "player_name": name,
                    "team": row.get("team_short", ""),
                    "position": row.get("position", ""),
                    "minutes": _to_json_value(row.get("minutes", 0)),
                    "goals": _to_json_value(row.get("goals", 0)),
                    "assists": _to_json_value(row.get("assists", 0)),
                    "xG": _to_json_value(row.get("xG", 0)),
                    "xA": _to_json_value(row.get("xA", 0)),
                    "now_cost": _to_json_value(row.get("now_cost", 0)),
                    "total_points": _to_json_value(row.get("total_points", 0)),
                    "xg_diff": _to_json_value(row.get("xg_diff", 0)),
                    "photo_url": photo_url,
                })

    return render_template(
        'watchlist.html',
        current_user=current_user,
        players=players,
        watchlist_count=len(watchlist),
    )

@watchlist_bp.route('/api/toggle', methods=['POST'])
@login_required
def toggle_watchlist():
    user_id = session.get('user_id')
    data = request.get_json() or {}
    player_name = (data.get('player_name') or '').strip()

    if not player_name:
        return jsonify({'error': 'player_name required'}), 400

    # Add or remove player from watchlist
    watchlist = get_watchlist(user_id)
    if player_name in watchlist:
        remove_from_watchlist(user_id, player_name)
        in_watchlist = False
    else:
        add_to_watchlist(user_id, player_name)
        in_watchlist = True

    return jsonify({'in_watchlist': in_watchlist, 'player_name': player_name})


@watchlist_bp.route('/api/status')
@login_required
def watchlist_status():
    # Check if a player is in the user's watchlist
    user_id = session.get('user_id')
    player_name = request.args.get('player_name', '').strip()
    if not player_name:
        return jsonify({'error': 'player_name required'}), 400
    watchlist = get_watchlist(user_id)
    return jsonify({'in_watchlist': player_name in watchlist})
