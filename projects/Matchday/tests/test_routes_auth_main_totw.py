from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
import routes.auth as auth_routes
import routes.main as main_routes
import routes.totw as totw_routes


def _make_client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def _login(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "tester"


def test_auth_login_get_renders(monkeypatch):
    client = _make_client()
    monkeypatch.setattr(auth_routes, "get_current_user", lambda: {"id": 1, "name": "tester"})

    response = client.get("/auth/login")

    assert response.status_code == 200


def test_auth_login_json_success(monkeypatch):
    client = _make_client()
    monkeypatch.setattr(auth_routes, "authenticate_user", lambda u, p: {"id": 9, "name": u})

    logged = {}

    def _capture_login(user):
        logged["user"] = user

    monkeypatch.setattr(auth_routes, "login_user", _capture_login)

    response = client.post(
        "/auth/login",
        json={"username": "  tester ", "password": " secret "},
    )

    payload = response.get_json()
    assert response.status_code == 200
    assert payload["success"] is True
    assert "Welcome" in payload["message"]
    assert logged["user"]["id"] == 9


def test_auth_login_json_failure(monkeypatch):
    client = _make_client()
    monkeypatch.setattr(auth_routes, "authenticate_user", lambda u, p: None)

    response = client.post("/auth/login", json={"username": "bad", "password": "bad"})

    payload = response.get_json()
    assert response.status_code == 200
    assert payload["success"] is False
    assert "Invalid" in payload["message"]


def test_auth_register_json_paths(monkeypatch):
    client = _make_client()

    monkeypatch.setattr(auth_routes, "register_user", lambda u, p: (True, "ok"))
    success_resp = client.post("/auth/register", json={"username": "new", "password": "pw"})

    monkeypatch.setattr(auth_routes, "register_user", lambda u, p: (False, "exists"))
    fail_resp = client.post("/auth/register", json={"username": "new", "password": "pw"})

    assert success_resp.status_code == 200
    assert success_resp.get_json() == {"success": True, "message": "ok"}
    assert fail_resp.status_code == 200
    assert fail_resp.get_json() == {"success": False, "message": "exists"}


def test_auth_register_form_success_redirect(monkeypatch):
    client = _make_client()
    monkeypatch.setattr(auth_routes, "register_user", lambda u, p: (True, "created"))

    response = client.post("/auth/register", data={"username": "a", "password": "b"}, follow_redirects=False)

    assert response.status_code in (301, 302)
    assert "/auth/login" in response.headers.get("Location", "")


def test_auth_logout_redirects_and_clears_session():
    client = _make_client()
    _login(client)

    response = client.get("/auth/logout", follow_redirects=False)

    assert response.status_code in (301, 302)
    assert "/" in response.headers.get("Location", "")
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_main_home_and_about(monkeypatch):
    client = _make_client()
    monkeypatch.setattr(main_routes, "get_current_user", lambda: {"id": 1, "name": "tester"})
    monkeypatch.setattr(main_routes, "get_3d_model_base64", lambda: "abc123")

    home = client.get("/")
    about = client.get("/about")

    assert home.status_code == 200
    assert about.status_code == 200


class _FakeFetcher:
    def get_current_gameweek(self):
        return 7


class _FakeProcessor:
    def __init__(self):
        self.fetcher = _FakeFetcher()

    def build_gameweek_dataframe(self, gameweek):
        return pd.DataFrame(
            {
                "player_name": ["A", "B", "C", "D"],
                "position": [1, 2, 3, 4],
                "rating": [9.5, 8.0, 7.2, 6.9],
            }
        )


class _FakeScorer:
    def calculate_scores(self, df):
        return df.copy()

    def calculate_rating(self, df):
        return df.copy()


class _FakeSelector:
    def select_best_xi_dynamic(self, df):
        return df, "4-3-3"


def test_totw_route_validates_gameweek_and_renders(monkeypatch):
    client = _make_client()

    monkeypatch.setattr(totw_routes, "DataProcessor", _FakeProcessor)
    monkeypatch.setattr(totw_routes, "TOTWScorer", _FakeScorer)
    monkeypatch.setattr(totw_routes, "FormationSelector", _FakeSelector)

    response = client.get("/totw/?gameweek=999")

    assert response.status_code == 200
    assert b"4-3-3" in response.data
