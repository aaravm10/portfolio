from pathlib import Path

from flask import Flask
from flask_session import Session

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')

    # Initialize session
    Session(app)

    # Create necessary directories
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    static_images_dir = Path("static/images")
    static_images_dir.mkdir(parents=True, exist_ok=True)

    # Register blueprints
    # Local imports avoid circular imports during app initialization.
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.totw import totw_bp
    from routes.create import create_bp
    from routes.leaderboards import leaderboards_bp
    from routes.watchlist import watchlist_bp
    from routes.fixtures import fixtures_bp
    from routes.optimize import optimize_bp
    from routes.help import help_bp

    blueprints = [
        main_bp,
        auth_bp,
        dashboard_bp,
        totw_bp,
        create_bp,
        leaderboards_bp,
        watchlist_bp,
        fixtures_bp,
        optimize_bp,
        help_bp,
    ]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    # Initialize database
    from models.user import init_db

    with app.app_context():
        init_db()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8080)