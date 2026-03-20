from pathlib import Path
import sys

from flask import Flask, Blueprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.auth import (
    get_current_user,
    get_user_display_name,
    is_logged_in,
    login_required,
    login_user,
    logout_user,
)
import utils.auth as auth_utils


def _app():
    app = Flask(__name__)
    app.config.update(SECRET_KEY="test")
    return app


def test_get_current_user_none_without_session():
    app = _app()
    with app.test_request_context("/"):
        assert get_current_user() is None


def test_get_current_user_reads_user(monkeypatch):
    app = _app()
    monkeypatch.setattr(auth_utils, "get_user_by_username", lambda username: {"name": username})

    with app.test_request_context("/"):
        from flask import session

        session["username"] = "tester"
        assert get_current_user() == {"name": "tester"}


def test_login_logout_and_is_logged_in():
    app = _app()

    with app.test_request_context("/"):
        from flask import session

        assert is_logged_in() is False
        login_user({"id": 1, "name": "tester"})
        assert session["user_id"] == 1
        assert session["username"] == "tester"
        assert session.permanent is True
        assert is_logged_in() is True
        assert get_user_display_name() == "tester"

        logout_user()
        assert is_logged_in() is False
        assert get_user_display_name() is None


def test_login_required_redirects_when_missing_session():
    app = _app()

    auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

    @auth_bp.route("/login")
    def login():
        return "login"

    app.register_blueprint(auth_bp)

    @app.route("/protected")
    @login_required
    def protected():
        return "ok"

    client = app.test_client()
    response = client.get("/protected", follow_redirects=False)

    assert response.status_code in (301, 302)
    assert "/auth/login" in response.headers.get("Location", "")


def test_login_required_allows_when_session_present():
    app = _app()

    auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

    @auth_bp.route("/login")
    def login():
        return "login"

    app.register_blueprint(auth_bp)

    @app.route("/protected")
    @login_required
    def protected():
        return "ok"

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get("/protected")
    assert response.status_code == 200
    assert response.data == b"ok"
