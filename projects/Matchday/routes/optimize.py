"""
Flask routes for Best XI Optimizer.
Greedy algorithm: maximize total_points / now_cost within budget and formation constraints.
"""

from flask import Blueprint, render_template, request, jsonify
from pathlib import Path
import pandas as pd

from utils.auth import get_current_user, login_required
from utils.charts import file_mtime, load_master_xlsx
from config import Config

optimize_bp = Blueprint('optimize', __name__, url_prefix='/optimize')

# Define formations and max players per club
FORMATIONS = {
    "4-3-3":   {"GKP": 1, "DEF": 4, "MID": 3, "FWD": 3},
    "4-4-2":   {"GKP": 1, "DEF": 4, "MID": 4, "FWD": 2},
    "3-5-2":   {"GKP": 1, "DEF": 3, "MID": 5, "FWD": 2},
    "4-2-3-1": {"GKP": 1, "DEF": 4, "MID": 5, "FWD": 1},
    "5-3-2":   {"GKP": 1, "DEF": 5, "MID": 3, "FWD": 2},
    "5-4-1":   {"GKP": 1, "DEF": 5, "MID": 4, "FWD": 1},
    "3-4-3":   {"GKP": 1, "DEF": 3, "MID": 4, "FWD": 3},
}

MAX_PER_CLUB = 3


def _load_master_df():
    xlsx_path = Path("data") / f"premier_league_master_{Config.SEASON}.xlsx"
    if not xlsx_path.exists():
        return None
    return load_master_xlsx(str(xlsx_path), file_mtime(xlsx_path)).copy()


def _build_optimal_xi(df, budget: float, formation: str) -> dict:
    """
    Greedy Best XI selection:
    1. Filter to players with valid cost and points
    2. Sort by value (total_points / now_cost) desc within each position
    3. Greedily pick players respecting formation, budget, and max 3 per club
    """
    pos_slots = FORMATIONS.get(formation, FORMATIONS["4-3-3"])

    # Clean and filter
    df = df.copy()
    if "now_cost" not in df.columns or "total_points" not in df.columns:
        return {"error": "FPL cost/points data not available. Please re-fetch data from the dashboard to update the dataset."}
    df = df[df["now_cost"].notna() & (df["now_cost"] > 0)]
    df = df[df["total_points"].notna() & (df["total_points"] > 0)]
    df = df[df["minutes"].fillna(0) >= 450]  # At least 5 full games

    if df.empty:
        return {"error": "No player data available. Please fetch data from the dashboard first."}

    df["value"] = df["total_points"] / df["now_cost"]
    df["player_name"] = df["player_name"].fillna("")
    df["team"] = df["team"].fillna("")
    df["team_short"] = df["team_short"].fillna("")

    # Variable to track selected players and club counts
    selected = []
    remaining_budget = budget
    club_counts: dict = {}

    # Using greedy technique to fill each position slot
    for pos, count in pos_slots.items():
        pos_players = df[df["position"] == pos].sort_values("value", ascending=False)
        picked = 0

        for _, row in pos_players.iterrows():
            if picked >= count:
                break
            cost = float(row["now_cost"])
            team = str(row["team"])
            if cost > remaining_budget:
                continue
            if club_counts.get(team, 0) >= MAX_PER_CLUB:
                continue

            def _safe_float(val, decimals=2):
                v = float(val) if pd.notna(val) else 0.0
                return round(v, decimals)

            def _safe_int(val):
                return int(val) if pd.notna(val) else 0

            selected.append({
                "player_name": row["player_name"],
                "team": row["team_short"],
                "full_team": team,
                "position": pos,
                "now_cost": round(cost, 1),
                "total_points": _safe_int(row["total_points"]),
                "goals": _safe_int(row.get("goals")),
                "assists": _safe_int(row.get("assists")),
                "xG": _safe_float(row.get("xG")),
                "form": _safe_float(row.get("form"), 1),
                "value": _safe_float(row["value"]),
            })
            remaining_budget = round(remaining_budget - cost, 1)
            club_counts[team] = club_counts.get(team, 0) + 1
            picked += 1

        if picked < count:
            return {"error": f"Could not fill {pos} slots (needed {count}, got {picked}). Try increasing budget or choosing a different formation."}

    # Calculate total cost
    total_cost = round(budget - remaining_budget, 1)
    total_pts = sum(p["total_points"] for p in selected)

    return {
        "formation": formation,
        "budget": budget,
        "total_cost": total_cost,
        "remaining_budget": round(remaining_budget, 1),
        "total_points": total_pts,
        "players": selected,
    }


@optimize_bp.route('/')
@login_required
def optimize_page():
    # Render the optimizer page with formation options
    current_user = get_current_user()
    return render_template(
        'optimize.html',
        current_user=current_user,
        formations=list(FORMATIONS.keys()),
    )


@optimize_bp.route('/api/build', methods=['POST'])
@login_required
def build_xi():
    # API endpoint to build optimal XI based on user input budget and formation
    data = request.get_json() or {}
    try:
        budget = float(data.get('budget', 83.0))
        formation = str(data.get('formation', '4-3-3'))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid parameters'}), 400

    # Validate budget and formation
    budget = max(60.0, min(budget, 110.0))
    if formation not in FORMATIONS:
        formation = '4-3-3'

    df = _load_master_df()
    if df is None:
        return jsonify({'error': 'No data available. Please fetch data from the dashboard first.'}), 404

    result = _build_optimal_xi(df, budget, formation)
    return jsonify(result)
