from flask import Blueprint, render_template, request
from totw import DataProcessor, TOTWScorer, FormationSelector
from utils.auth import get_current_user

totw_bp = Blueprint('totw', __name__, url_prefix='/totw')

@totw_bp.route('/')
def totw_page():
    gameweek = request.args.get('gameweek', type=int)
    
    processor = DataProcessor()
    scorer = TOTWScorer()
    selector = FormationSelector()
    
    # Get current gameweek
    current_gw = processor.fetcher.get_current_gameweek()
    
    # Validate gameweek
    if gameweek is None or gameweek < 1 or gameweek > current_gw:
        gameweek = current_gw
    
    df = processor.build_gameweek_dataframe(gameweek)
    df = scorer.calculate_scores(df)
    
    best_xi, formation = selector.select_best_xi_dynamic(df)
    best_xi = scorer.calculate_rating(best_xi)
    
    # Mark the top performer (highest rating)
    best_xi = best_xi.copy()
    max_rating = best_xi['rating'].max()
    best_xi['is_top_performer'] = best_xi['rating'] == max_rating
    
    by_position = {
        'goalkeepers': best_xi[best_xi['position'] == 1].to_dict('records'),
        'defenders': best_xi[best_xi['position'] == 2].to_dict('records'),
        'midfielders': best_xi[best_xi['position'] == 3].to_dict('records'),
        'forwards': best_xi[best_xi['position'] == 4].to_dict('records')
    }

    current_user = get_current_user()
    
    return render_template('totw.html',
                         current_user=current_user,
                         gameweek=gameweek,
                         current_gw=current_gw,
                         formation=formation,
                         by_position=by_position)