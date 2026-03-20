"""
Flask routes for Leaderboards feature
"""

from flask import Blueprint, render_template, request
from leaderboards import LeaderboardsProcessor
from utils.auth import get_current_user
from utils.charts import file_mtime, load_master_xlsx, compute_percentiles
from pathlib import Path
from config import Config

leaderboards_bp = Blueprint('leaderboards', __name__, url_prefix='/leaderboards')

# Leaderboard views
VALID_VIEWS = ['players', 'teams', 'percentiles', 'value', 'xg']

# load master DataFrame with caching, used for percentile and value leaderboards
def _load_master_df():
    xlsx_path = Path("data") / f"premier_league_master_{Config.SEASON}.xlsx"
    if not xlsx_path.exists():
        return None
    return load_master_xlsx(str(xlsx_path), file_mtime(xlsx_path)).copy()

def _get_percentile_table():
    """Build a percentile table for outfield players (position != GKP)."""
    df = _load_master_df()
    if df is None:
        return []

    df = df[df["minutes"].fillna(0) >= 450].copy()
    metrics = [
        "goals_p90", "xG_p90", "shots_p90",
        "assists_p90", "xA_p90", "key_passes_p90",
        "influence", "creativity", "threat", "ict_index",
    ]

    # Only include metrics that are present in the DataFrame
    metrics = [m for m in metrics if m in df.columns]
    df_pct = compute_percentiles(df, metrics, group_col="position")

    rows = []

    # Build percentile table
    for _, row in df_pct.iterrows():
        entry = {
            "player_name": row.get("player_name", ""),
            "team_short": row.get("team_short", ""),
            "position": row.get("position", ""),
            "minutes": int(row.get("minutes", 0) or 0),
        }
        for m in metrics:
            pct_col = m + "_pct"
            entry[pct_col] = round(float(row.get(pct_col, 0) or 0), 0)
        rows.append(entry)

    # Sort by goals percentile as a default, then take top 100
    rows.sort(key=lambda r: r.get("goals_p90_pct", 0), reverse=True)
    return rows[:100], metrics

def _get_value_leaderboard():
    """Top players by FPL points per £m."""
    df = _load_master_df()
    if df is None:
        return []

    # Filter to players with valid cost and points, and at least 450 minutes
    df = df[df["now_cost"].notna() & (df["now_cost"] > 0)].copy()
    df = df[df["total_points"].notna() & (df["total_points"] > 0)].copy()
    df = df[df["minutes"].fillna(0) >= 450].copy()

    df["value_pts"] = df["total_points"] / df["now_cost"]

    # Get top 5 for each position
    positions = {"GKP": [], "DEF": [], "MID": [], "FWD": []}
    for pos in positions:
        top = df[df["position"] == pos].nlargest(5, "value_pts")
        for rank, (_, row) in enumerate(top.iterrows(), 1):
            positions[pos].append({
                "rank": rank,
                "player_name": row.get("player_name", ""),
                "team_short": row.get("team_short", ""),
                "value": round(float(row["value_pts"]), 2),
                "now_cost": round(float(row.get("now_cost", 0)), 1),
                "total_points": int(row.get("total_points", 0)),
            })

    return positions


def _get_xg_diff_leaderboard():
    """Top over- and under-performers vs xG."""
    df = _load_master_df()
    if df is None:
        return [], []

    # Filter to players with valid cost and points, and at least 450 minutes
    df = df[df["xG"].notna() & (df["xG"] > 0)].copy()
    df = df[df["minutes"].fillna(0) >= 450].copy()
    df["xg_diff"] = df["goals"] - df["xG"]

    # Get top 10 over- and under-performers
    over = df.nlargest(10, "xg_diff")[
        ["player_name", "team_short", "position", "goals", "xG", "xg_diff"]
    ].to_dict("records")
    under = df.nsmallest(10, "xg_diff")[
        ["player_name", "team_short", "position", "goals", "xG", "xg_diff"]
    ].to_dict("records")

    for row in over + under:
        row["goals"] = int(row.get("goals", 0) or 0)
        row["xG"] = round(float(row.get("xG", 0) or 0), 2)
        row["xg_diff"] = round(float(row.get("xg_diff", 0) or 0), 2)

    return over, under


@leaderboards_bp.route('/')
def leaderboards_page():
    """
    Main leaderboards page.

    Query params:
    - view: 'players' | 'teams' | 'percentiles' | 'value' | 'xg'
    """
    current_user = get_current_user()

    view = request.args.get('view', 'players')
    if view not in VALID_VIEWS:
        view = 'players'

    processor = LeaderboardsProcessor()

    # Leaderboard data variables
    leaderboards_data = {}
    percentile_rows = []
    percentile_metrics = []
    value_data = {}
    xg_over = []
    xg_under = []
    error_message = None

    try:
        if view == 'players':
            leaderboards_data = processor.get_player_leaderboards()
        elif view == 'teams':
            leaderboards_data = processor.get_team_leaderboards()
        elif view == 'percentiles':
            result = _get_percentile_table()
            percentile_rows, percentile_metrics = result if result else ([], [])
        elif view == 'value':
            value_data = _get_value_leaderboard()
        elif view == 'xg':
            xg_over, xg_under = _get_xg_diff_leaderboard()

    except Exception as e:
        error_message = f"Error loading leaderboards: {str(e)}"

    return render_template(
        'leaderboards.html',
        current_user=current_user,
        view=view,
        leaderboards=leaderboards_data,
        percentile_rows=percentile_rows,
        percentile_metrics=percentile_metrics,
        value_data=value_data,
        xg_over=xg_over,
        xg_under=xg_under,
        error=error_message,
    )