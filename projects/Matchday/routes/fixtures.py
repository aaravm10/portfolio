"""
Flask routes for Fixture Difficulty Rating (FDR) and Match Predictor.
"""

from flask import Blueprint, render_template, request, jsonify
from pathlib import Path

from utils.auth import get_current_user, login_required
from utils.fixtures_data import get_fdr_matrix, get_team_id_map, get_current_gameweek, predict_match
from utils.charts import file_mtime, load_master_xlsx
from config import Config

fixtures_bp = Blueprint('fixtures', __name__, url_prefix='/fixtures')


def _load_master_df():
    xlsx_path = Path("data") / f"premier_league_master_{Config.SEASON}.xlsx"
    if not xlsx_path.exists():
        return None
    return load_master_xlsx(str(xlsx_path), file_mtime(xlsx_path)).copy()


@fixtures_bp.route('/')
@login_required
def fixtures_page():
    current_user = get_current_user()

    try:
        team_map = get_team_id_map()
        fdr = get_fdr_matrix(n_upcoming=10)
        current_gw = get_current_gameweek()

        # Determine which gameweeks to show (next 10 from current)
        all_gws = sorted({fix["gw"] for fixes in fdr.values() for fix in fixes})

        # Build sorted list of teams with their FDR rows
        teams_fdr = []
        for tid, team_info in sorted(team_map.items(), key=lambda x: x[1]["name"]):
            fixtures_list = fdr.get(tid, [])
            # Build a gw->fix lookup for easy template access
            gw_map = {fix["gw"]: fix for fix in fixtures_list}
            teams_fdr.append({
                "team_id": tid,
                "team_name": team_info["name"],
                "team_short": team_info["short_name"],
                "badge_url": team_info["badge_url"],
                "fixtures": [gw_map.get(gw) for gw in all_gws],
            })

        return render_template(
            'fixtures.html',
            current_user=current_user,
            teams_fdr=teams_fdr,
            gameweeks=all_gws,
            current_gw=current_gw,
            team_map=team_map,
        )
    except Exception as e:
        return render_template(
            'fixtures.html',
            current_user=current_user,
            error=str(e),
            teams_fdr=[],
            gameweeks=[],
            current_gw=1,
            team_map={},
        )


@fixtures_bp.route('/api/predict', methods=['POST'])
@login_required
def predict():
    data = request.get_json() or {}
    try:
        team_h_id = int(data.get('team_h_id', 0))
        team_a_id = int(data.get('team_a_id', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid team IDs'}), 400

    if not team_h_id or not team_a_id:
        return jsonify({'error': 'Both team_h_id and team_a_id are required'}), 400

    if team_h_id == team_a_id:
        return jsonify({'error': 'Teams must be different'}), 400

    df = _load_master_df()
    result = predict_match(team_h_id, team_a_id, df)
    return jsonify(result)
