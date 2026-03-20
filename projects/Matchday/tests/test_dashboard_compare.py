from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
import routes.dashboard as dashboard_routes


def _sample_master_df():
    return pd.DataFrame(
        {
            "player_name": ["Player One", "Player Two", "Player Three"],
            "team": ["Arsenal", "Chelsea", "Arsenal"],
            "team_short": ["ARS", "CHE", "ARS"],
            "position": ["MID", "FWD", "DEF"],
            "minutes": [900, 850, 700],
            "starts": [10, 9, 8],
            "goals": [5, 7, 1],
            "assists": [3, 1, 2],
            "xG": [4.2, 6.0, 0.8],
            "xA": [2.1, 1.5, 1.9],
            "shots": [20, 30, 5],
            "key_passes": [15, 8, 10],
            "influence": [100, 110, 90],
            "creativity": [200, 120, 180],
            "threat": [300, 500, 75],
            "ict_index": [400, 510, 220],
            "goals_p90": [0.5, 0.74, 0.13],
            "assists_p90": [0.3, 0.1, 0.26],
            "xG_p90": [0.42, 0.64, 0.10],
            "xA_p90": [0.21, 0.18, 0.24],
            "shots_p90": [2.0, 3.2, 0.64],
            "key_passes_p90": [1.5, 0.9, 1.29],
        }
    )


def _make_client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def _login(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "tester"


def test_dashboard_index_requires_login():
    client = _make_client()

    response = client.get("/dashboard/")

    assert response.status_code in (301, 302)
    assert "/auth/login" in response.headers.get("Location", "")


def test_compare_options_players_search(monkeypatch):
    client = _make_client()
    _login(client)
    monkeypatch.setattr(dashboard_routes, "_load_dashboard_dataframe", lambda: _sample_master_df())

    response = client.get("/dashboard/api/compare/options?mode=players&query=two")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["mode"] == "players"
    assert payload["options"] == ["Player Two"]


def test_compare_players_returns_payload(monkeypatch):
    client = _make_client()
    _login(client)
    monkeypatch.setattr(dashboard_routes, "_load_dashboard_dataframe", lambda: _sample_master_df())

    response = client.get(
        "/dashboard/api/compare?mode=players&entity_a=Player%20One&entity_b=Player%20Two"
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["mode"] == "players"
    assert payload["entity_a"]["name"] == "Player One"
    assert payload["entity_b"]["name"] == "Player Two"
    stats = payload["stats"]
    assert any(s["metric"] == "goals" for s in stats)


def test_compare_players_rejects_same_entity(monkeypatch):
    client = _make_client()
    _login(client)
    monkeypatch.setattr(dashboard_routes, "_load_dashboard_dataframe", lambda: _sample_master_df())

    response = client.get(
        "/dashboard/api/compare?mode=players&entity_a=Player%20One&entity_b=Player%20One"
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "cannot be the same" in payload["error"].lower()


def test_compare_teams_returns_payload(monkeypatch):
    client = _make_client()
    _login(client)
    monkeypatch.setattr(dashboard_routes, "_load_dashboard_dataframe", lambda: _sample_master_df())

    response = client.get(
        "/dashboard/api/compare?mode=teams&entity_a=Arsenal&entity_b=Chelsea"
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["mode"] == "teams"
    assert payload["entity_a"]["name"] == "Arsenal"
    assert payload["entity_b"]["name"] == "Chelsea"
    assert any(s["metric"] == "goals" for s in payload["stats"])
