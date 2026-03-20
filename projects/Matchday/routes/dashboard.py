from flask import Blueprint, jsonify, render_template, request, session
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

from pipeline import MasterPipeline, write_excel
from utils.auth import get_current_user, login_required
from utils.charts import (
    file_mtime, load_master_xlsx, compute_percentiles,
    build_radial_figure, figure_to_base64
)
from utils.player_history import fetch_player_history, get_form_stats, get_cumulative_timeline
from models.user import get_watchlist
from config import Config

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

ID_COLUMNS = {"fpl_id", "understat_id"}
MEAN_TEAM_STATS = {"influence", "creativity", "threat", "ict_index"}


def _master_xlsx_path():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir / f"premier_league_master_{Config.SEASON}.xlsx"


def _load_dashboard_dataframe():
    xlsx_path = _master_xlsx_path()
    if not xlsx_path.exists():
        return None

    df = load_master_xlsx(str(xlsx_path), file_mtime(xlsx_path)).copy()
    df["player_name"] = df["player_name"].fillna("")
    df["team"] = df["team"].fillna("")
    df["team_short"] = df["team_short"].fillna("")
    df["position"] = df["position"].fillna("")
    return df


def _require_dashboard_dataframe():
    """Load dashboard data once and provide a consistent 404 payload if missing."""
    df = _load_dashboard_dataframe()
    if df is None:
        return None, (jsonify({'error': 'Data not available'}), 404)
    return df, None


def _select_compare_stat_columns(df):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    excluded = ID_COLUMNS
    return [c for c in numeric_cols if c not in excluded]


def _to_json_value(value):
    if pd.isna(value):
        return 0
    value = float(value)
    return int(value) if value.is_integer() else round(value, 2)


def _normalize_name(value):
    return (value or "").strip().lower()


def _resolve_exact_or_case_insensitive(options, raw_name):
    if raw_name in options:
        return raw_name

    raw_normalized = _normalize_name(raw_name)
    for option in options:
        if _normalize_name(option) == raw_normalized:
            return option
    return None


def _build_player_entity(df, player_name, stat_cols):
    player_rows = df[df["player_name"] == player_name]
    if player_rows.empty:
        return None

    row = player_rows.iloc[0]
    stats = {metric: _to_json_value(row.get(metric, 0)) for metric in stat_cols}

    return {
        "name": player_name,
        "type": "player",
        "subtitle": f"{row.get('team_short', '')} · {row.get('position', '')}",
        "stats": stats,
    }


def _build_team_entity(df, team_name, stat_cols):
    team_rows = df[df["team"] == team_name]
    if team_rows.empty:
        return None

    aggregate_stats = {}
    for metric in stat_cols:
        values = team_rows[metric].dropna()
        if values.empty:
            aggregate_stats[metric] = 0
            continue

        if metric.endswith("_p90") or metric in MEAN_TEAM_STATS:
            aggregate_stats[metric] = _to_json_value(values.mean())
        else:
            aggregate_stats[metric] = _to_json_value(values.sum())

    return {
        "name": team_name,
        "type": "team",
        "subtitle": f"{len(team_rows)} players",
        "stats": aggregate_stats,
    }

@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard main page"""
    current_user = get_current_user()
    
    # Set up data directory and file path
    xlsx_path = _master_xlsx_path()
    
    # Check if data needs to be fetched
    data_exists = xlsx_path.exists()
    mtime = file_mtime(xlsx_path) if data_exists else 0
    updated = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S") if mtime else "unknown"
    
    # If no data exists, we'll show a loading page that triggers data fetch
    if not data_exists:
        return render_template('dashboard/loading.html', 
                             current_user=current_user)
    
    # Load and prepare data
    try:
        df = load_master_xlsx(str(xlsx_path), mtime)
        df = df.copy()
        df["player_name"] = df["player_name"].fillna("")
        df["team"] = df["team"].fillna("")
        df["team_short"] = df["team_short"].fillna("")
        df["position"] = df["position"].fillna("")
        
        teams = sorted([t for t in df["team"].dropna().unique().tolist() if t != ""])
        
        return render_template('dashboard/index.html', 
                             current_user=current_user,
                             teams=teams,
                             updated=updated,
                             total_players=len(df))
    
    except Exception as e:
        return render_template('dashboard/error.html', 
                             current_user=current_user,
                             error=str(e))

@dashboard_bp.route('/fetch-data')
@login_required
def fetch_data():
    """Fetch Premier League data via AJAX"""
    xlsx_path = _master_xlsx_path()
    
    try:
        pipeline = MasterPipeline()
        frames = pipeline.build_master(season=int(Config.SEASON))
        write_excel(frames, xlsx_path)
        
        return jsonify({
            'success': True, 
            'message': 'Data fetched successfully',
            'redirect_url': '/dashboard'
        })
    
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error fetching data: {str(e)}'
        })

@dashboard_bp.route('/api/players')
@login_required
def get_players():
    """API endpoint to get filtered player data"""
    # Get filter parameters
    search = request.args.get('search', '').strip()
    team = request.args.get('team', 'All')
    positions = request.args.getlist('position')
    minutes_min = int(request.args.get('minutes_min', 0))
    sort_by = request.args.get('sort_by', 'minutes')
    sort_desc = request.args.get('sort_desc', 'true').lower() == 'true'
    
    # Load data
    df, error_response = _require_dashboard_dataframe()
    if error_response is not None:
        return error_response
    
    try:
        df = df.copy()
        
        # Apply filters
        df = df[df["minutes"].fillna(0) >= minutes_min]
        
        if positions:
            df = df[df["position"].isin(positions)]
        
        if team != "All":
            df = df[df["team"] == team]
        
        if search:
            mask = df["player_name"].str.contains(search, case=False, na=False)
            df = df[mask]
        
        # Sort data
        if sort_by in df.columns:
            df = df.sort_values(sort_by, ascending=not sort_desc, na_position="last")
        
        # Select display columns
        display_cols = [
            "player_name", "team_short", "position", "minutes", "goals", "assists",
            "xG", "xA", "shots", "key_passes", "influence", "creativity", "threat", "ict_index"
        ]
        display_cols = [c for c in display_cols if c in df.columns]
        
        # Convert to dict for JSON response
        df_display = df[display_cols].head(100)  # Limit to 100 rows for performance
        
        # Handle NaN values for JSON serialization
        df_display = df_display.fillna('')
        
        players_data = df_display.to_dict('records')
        
        return jsonify({
            'players': players_data,
            'total': len(df),
            'filtered': len(df_display)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/player/<player_name>')
@login_required
def get_player_details(player_name):
    """Get detailed player information"""
    # Load data
    df, error_response = _require_dashboard_dataframe()
    if error_response is not None:
        return error_response
    
    try:
        # Find player
        player_mask = df["player_name"] == player_name
        if not player_mask.any():
            return jsonify({'error': 'Player not found'}), 404
        
        row = df[player_mask].iloc[0]
        
        # Basic player info
        player_info = {
            'name': row.get('player_name', ''),
            'team': row.get('team_short', ''),
            'position': row.get('position', ''),
            'minutes': int(row.get('minutes', 0) if pd.notna(row.get('minutes')) else 0),
            'starts': int(row.get('starts', 0) if pd.notna(row.get('starts')) else 0),
        }
        
        # Key stats for overview
        key_stats = [
            "goals", "assists", "xG", "xA", "shots", "key_passes",
            "clean_sheets", "saves", "influence", "creativity", "threat", "ict_index"
        ]
        overview_data = []
        for stat in key_stats:
            if stat in df.columns:
                value = row.get(stat)
                overview_data.append({
                    'metric': stat,
                    'value': _to_json_value(value)
                })
        
        # Percentile calculation
        metrics = ["goals_p90", "xG_p90", "shots_p90", "assists_p90", "xA_p90", 
                  "key_passes_p90", "influence", "creativity", "threat", "ict_index"]
        metrics = [m for m in metrics if m in df.columns]
        
        df_pct = compute_percentiles(df, metrics, group_col="position")
        
        # Find percentile row
        id_col = "fpl_id" if "fpl_id" in df_pct.columns else ("understat_id" if "understat_id" in df_pct.columns else None)
        
        if id_col is not None and id_col in df_pct.columns and pd.notna(row.get(id_col)):
            row_pct = df_pct[df_pct[id_col] == row.get(id_col)].iloc[0]
        else:
            row_pct = df_pct[df_pct["player_name"] == player_name].iloc[0]
        
        # Build percentile data
        percentile_data = []
        metric_names = ["goals_p90", "xG_p90", "shots_p90", "assists_p90", "xA_p90", 
                       "key_passes_p90", "influence", "creativity", "threat", "ict_index"]
        
        for m in metric_names:
            percentile = row_pct.get(m + "_pct") if m in metrics else np.nan
            value = row.get(m) if m in df.columns else np.nan
            percentile_data.append({
                'metric': m,
                'percentile': _to_json_value(percentile),
                'value': _to_json_value(value)
            })
        
        return jsonify({
            'player_info': player_info,
            'overview': overview_data,
            'percentiles': percentile_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/player/<player_name>/chart')
@login_required
def get_player_chart(player_name):
    """Generate radial chart for player"""
    # Load data
    df, error_response = _require_dashboard_dataframe()
    if error_response is not None:
        return error_response
    
    try:
        # Find player
        player_mask = df["player_name"] == player_name
        if not player_mask.any():
            return jsonify({'error': 'Player not found'}), 404
        
        row = df[player_mask].iloc[0]
        
        # Calculate percentiles
        metrics = ["goals_p90", "xG_p90", "shots_p90", "assists_p90", "xA_p90", 
                  "key_passes_p90", "influence", "creativity", "threat", "ict_index"]
        metrics = [m for m in metrics if m in df.columns]
        
        df_pct = compute_percentiles(df, metrics, group_col="position")
        
        # Find percentile row
        id_col = "fpl_id" if "fpl_id" in df_pct.columns else ("understat_id" if "understat_id" in df_pct.columns else None)
        
        if id_col is not None and id_col in df_pct.columns and pd.notna(row.get(id_col)):
            row_pct = df_pct[df_pct[id_col] == row.get(id_col)].iloc[0]
        else:
            row_pct = df_pct[df_pct["player_name"] == player_name].iloc[0]
        
        # Keep labels/metrics paired so optional missing columns do not desync chart inputs.
        metric_specs = [
            ("goals_p90", "G/90"),
            ("xG_p90", "xG/90"),
            ("shots_p90", "Sh/90"),
            ("assists_p90", "A/90"),
            ("xA_p90", "xA/90"),
            ("key_passes_p90", "KP/90"),
            ("influence", "Inf"),
            ("creativity", "Cre"),
            ("threat", "Thr"),
            ("ict_index", "ICT"),
        ]
        active_specs = [(m, label) for m, label in metric_specs if m in metrics]

        labels_radial = ["G/90", "xG/90", "Sh/90", "A/90", "xA/90", "KP/90", "Inf", "Cre", "Thr", "ICT"]
        pct_vals = []
        for metric_name, _ in active_specs:
            v = row_pct.get(metric_name + "_pct")
            pct_vals.append(float(v) / 100.0 if pd.notna(v) else 0.0)

        labels_radial = [label for _, label in active_specs]
        colors = [
            "#f6a019", "#f6a019", "#f6a019",  # Goals/xG/Shots
            "#2aa7ff", "#2aa7ff", "#2aa7ff",  # Assists/xA/Key passes
            "#1c6dd0", "#1c6dd0", "#1c6dd0", "#1c6dd0"  # Influence/Creativity/Threat/ICT
        ]
        colors = colors[:len(labels_radial)]
        group_bounds = [3, 6]
        
        # Generate chart
        fig = build_radial_figure(labels_radial, pct_vals, colors, group_bounds, Config.AX_BG)
        chart_data = figure_to_base64(fig)
        
        return jsonify({
            'chart_data': chart_data,
            'player_name': player_name,
            'team': row.get('team_short', ''),
            'position': row.get('position', '')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/compare/options')
@login_required
def get_compare_options():
    """Get searchable compare options for players or teams."""
    mode = request.args.get('mode', 'players').strip().lower()
    query = request.args.get('query', '').strip().lower()

    if mode not in {'players', 'teams'}:
        return jsonify({'error': 'Invalid mode. Use players or teams.'}), 400

    df = _load_dashboard_dataframe()
    if df is None:
        return jsonify({'error': 'Data not available'}), 404

    source_col = 'player_name' if mode == 'players' else 'team'
    options = sorted([item for item in df[source_col].dropna().unique().tolist() if str(item).strip()])

    if query:
        options = [item for item in options if query in str(item).lower()]

    return jsonify({
        'mode': mode,
        'options': options[:20]
    })


@dashboard_bp.route('/api/compare')
@login_required
def compare_entities():
    """Compare two players or two teams side-by-side."""
    mode = request.args.get('mode', 'players').strip().lower()
    entity_a_raw = request.args.get('entity_a', '').strip()
    entity_b_raw = request.args.get('entity_b', '').strip()

    if mode not in {'players', 'teams'}:
        return jsonify({'error': 'Invalid mode. Use players or teams.'}), 400

    if not entity_a_raw or not entity_b_raw:
        return jsonify({'error': 'Both entity_a and entity_b are required.'}), 400

    if _normalize_name(entity_a_raw) == _normalize_name(entity_b_raw):
        return jsonify({'error': 'Compared entities cannot be the same.'}), 400

    df = _load_dashboard_dataframe()
    if df is None:
        return jsonify({'error': 'Data not available'}), 404

    source_col = 'player_name' if mode == 'players' else 'team'
    all_options = [item for item in df[source_col].dropna().unique().tolist() if str(item).strip()]

    entity_a_name = _resolve_exact_or_case_insensitive(all_options, entity_a_raw)
    entity_b_name = _resolve_exact_or_case_insensitive(all_options, entity_b_raw)

    if not entity_a_name or not entity_b_name:
        return jsonify({'error': f'One or both {mode[:-1]} values were not found.'}), 404

    stat_cols = _select_compare_stat_columns(df)

    if mode == 'players':
        entity_a = _build_player_entity(df, entity_a_name, stat_cols)
        entity_b = _build_player_entity(df, entity_b_name, stat_cols)
    else:
        entity_a = _build_team_entity(df, entity_a_name, stat_cols)
        entity_b = _build_team_entity(df, entity_b_name, stat_cols)

    if entity_a is None or entity_b is None:
        return jsonify({'error': 'Unable to build comparison payload.'}), 404

    stats = []
    for metric in stat_cols:
        value_a = entity_a['stats'].get(metric, 0)
        value_b = entity_b['stats'].get(metric, 0)
        stats.append({
            'metric': metric,
            'value_a': value_a,
            'value_b': value_b,
            'diff': _to_json_value(value_a - value_b),
        })

    return jsonify({
        'mode': mode,
        'entity_a': {
            'name': entity_a['name'],
            'type': entity_a['type'],
            'subtitle': entity_a['subtitle'],
        },
        'entity_b': {
            'name': entity_b['name'],
            'type': entity_b['type'],
            'subtitle': entity_b['subtitle'],
        },
        'stats': stats,
    })


@dashboard_bp.route('/api/player/<player_name>/form')
@login_required
def get_player_form(player_name):
    """Return last 5 gameweek stats for a player (from FPL element-summary API)."""
    df = _load_dashboard_dataframe()
    if df is None:
        return jsonify({'error': 'Data not available'}), 404

    player_mask = df["player_name"] == player_name
    if not player_mask.any():
        return jsonify({'error': 'Player not found'}), 404

    row = df[player_mask].iloc[0]
    fpl_id = row.get("fpl_id")

    if pd.isna(fpl_id):
        return jsonify({'error': 'No FPL ID for this player'}), 404

    history = fetch_player_history(int(fpl_id))
    form = get_form_stats(history, n_gw=5)

    return jsonify({
        'player_name': player_name,
        'fpl_id': int(fpl_id),
        **form,
    })


@dashboard_bp.route('/api/player/<player_name>/timeline')
@login_required
def get_player_timeline(player_name):
    """Return cumulative season stats per gameweek for a player."""
    df = _load_dashboard_dataframe()
    if df is None:
        return jsonify({'error': 'Data not available'}), 404

    player_mask = df["player_name"] == player_name
    if not player_mask.any():
        return jsonify({'error': 'Player not found'}), 404

    row = df[player_mask].iloc[0]
    fpl_id = row.get("fpl_id")

    if pd.isna(fpl_id):
        return jsonify({'error': 'No FPL ID for this player'}), 404

    history = fetch_player_history(int(fpl_id))
    timeline = get_cumulative_timeline(history)

    return jsonify({
        'player_name': player_name,
        'timeline': timeline,
    })


@dashboard_bp.route('/api/player/<player_name>/team-radar')
@login_required
def get_team_radar(player_name):
    """Return team-level radar chart as base64 for the team of the given player."""
    df = _load_dashboard_dataframe()
    if df is None:
        return jsonify({'error': 'Data not available'}), 404

    player_mask = df["player_name"] == player_name
    if not player_mask.any():
        return jsonify({'error': 'Player not found'}), 404

    row = df[player_mask].iloc[0]
    team_name = row.get("team", "")

    team_rows = df[df["team"] == team_name]
    if team_rows.empty:
        return jsonify({'error': 'Team not found'}), 404

    # Compute team-level aggregated percentiles against all teams
    metrics = ["goals_p90", "xG_p90", "shots_p90", "assists_p90", "xA_p90",
               "key_passes_p90", "influence", "creativity", "threat", "ict_index"]
    metrics = [m for m in metrics if m in df.columns]

    # Build a team-aggregate df for all teams
    team_agg_rows = []
    for tname in df["team"].dropna().unique():
        trows = df[df["team"] == tname]
        agg = {"team": tname}
        for m in metrics:
            vals = trows[m].dropna()
            agg[m] = float(vals.mean()) if not vals.empty else 0.0
        team_agg_rows.append(agg)

    team_agg_df = pd.DataFrame(team_agg_rows)

    df_pct = compute_percentiles(team_agg_df, metrics)
    target_row = df_pct[df_pct["team"] == team_name]
    if target_row.empty:
        return jsonify({'error': 'Could not compute team percentiles'}), 500

    target_row = target_row.iloc[0]

    labels_radial = ["G/90", "xG/90", "Sh/90", "A/90", "xA/90", "KP/90", "Inf", "Cre", "Thr", "ICT"]
    pct_vals = []
    for m in metrics:
        v = target_row.get(m + "_pct")
        pct_vals.append(float(v) / 100.0 if pd.notna(v) else 0.0)

    colors = [
        "#f6a019", "#f6a019", "#f6a019",
        "#2aa7ff", "#2aa7ff", "#2aa7ff",
        "#1c6dd0", "#1c6dd0", "#1c6dd0", "#1c6dd0"
    ]
    group_bounds = [3, 6]

    fig = build_radial_figure(labels_radial, pct_vals, colors, group_bounds, Config.AX_BG)
    chart_data = figure_to_base64(fig)

    return jsonify({
        'chart_data': chart_data,
        'team': team_name,
        'team_short': row.get('team_short', ''),
    })


@dashboard_bp.route('/api/watchlist-status')
@login_required
def watchlist_status():
    """Return whether the given player is in the current user's watchlist."""
    player_name = request.args.get('player_name', '').strip()
    if not player_name:
        return jsonify({'error': 'player_name required'}), 400
    user_id = session.get('user_id')
    watchlist = get_watchlist(user_id)
    return jsonify({'in_watchlist': player_name in watchlist})