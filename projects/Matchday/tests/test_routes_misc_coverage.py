from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
import routes.optimize as optimize_routes
import routes.fixtures as fixtures_routes
import routes.help as help_routes
import routes.create as create_routes
import routes.leaderboards as leaderboards_routes


def _client_logged_in():
    app = create_app()
    app.config.update(TESTING=True)
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "tester"
    return client


def _sample_master_players():
    rows = []
    # 1 GK
    rows.append(
        {
            "player_name": "GK1",
            "position": "GKP",
            "team": "Arsenal",
            "team_short": "ARS",
            "now_cost": 5.0,
            "total_points": 100,
            "minutes": 900,
            "goals": 0,
            "assists": 0,
            "xG": 0.1,
            "form": 4.5,
        }
    )

    for i in range(1, 5):
        rows.append(
            {
                "player_name": f"DEF{i}",
                "position": "DEF",
                "team": f"TeamD{i}",
                "team_short": f"D{i}",
                "now_cost": 5.0,
                "total_points": 90 + i,
                "minutes": 900,
                "goals": 1,
                "assists": 2,
                "xG": 1.0,
                "form": 5.0,
            }
        )

    for i in range(1, 4):
        rows.append(
            {
                "player_name": f"MID{i}",
                "position": "MID",
                "team": f"TeamM{i}",
                "team_short": f"M{i}",
                "now_cost": 7.0,
                "total_points": 110 + i,
                "minutes": 900,
                "goals": 6,
                "assists": 5,
                "xG": 5.0,
                "form": 6.0,
            }
        )

    for i in range(1, 4):
        rows.append(
            {
                "player_name": f"FWD{i}",
                "position": "FWD",
                "team": f"TeamF{i}",
                "team_short": f"F{i}",
                "now_cost": 8.0,
                "total_points": 120 + i,
                "minutes": 900,
                "goals": 10,
                "assists": 2,
                "xG": 8.0,
                "form": 6.5,
            }
        )

    return pd.DataFrame(rows)


def test_optimize_build_optimal_xi_success_and_error_paths():
    df = _sample_master_players()

    result = optimize_routes._build_optimal_xi(df, budget=100.0, formation="4-3-3")
    assert "players" in result
    assert len(result["players"]) == 11

    missing = optimize_routes._build_optimal_xi(pd.DataFrame({"a": [1]}), budget=90, formation="4-3-3")
    assert "error" in missing


def test_optimize_routes_api(monkeypatch):
    client = _client_logged_in()

    monkeypatch.setattr(optimize_routes, "_load_master_df", lambda: _sample_master_players())

    good = client.post("/optimize/api/build", json={"budget": 95, "formation": "4-3-3"})
    assert good.status_code == 200
    assert "players" in good.get_json()

    bad = client.post("/optimize/api/build", json={"budget": "nope", "formation": "4-3-3"})
    assert bad.status_code == 400


def test_fixtures_routes_success_error_and_predict(monkeypatch):
    client = _client_logged_in()

    monkeypatch.setattr(
        fixtures_routes,
        "get_team_id_map",
        lambda: {
            1: {"name": "Arsenal", "short_name": "ARS", "badge_url": "x"},
            2: {"name": "Chelsea", "short_name": "CHE", "badge_url": "y"},
        },
    )
    monkeypatch.setattr(
        fixtures_routes,
        "get_fdr_matrix",
        lambda n_upcoming=10: {
            1: [{"gw": 30, "opponent_id": 2, "difficulty": 2, "is_home": True}],
            2: [{"gw": 30, "opponent_id": 1, "difficulty": 4, "is_home": False}],
        },
    )
    monkeypatch.setattr(fixtures_routes, "get_current_gameweek", lambda: 30)

    ok = client.get("/fixtures/")
    assert ok.status_code == 200

    monkeypatch.setattr(fixtures_routes, "_load_master_df", lambda: pd.DataFrame({"x": [1]}))
    monkeypatch.setattr(fixtures_routes, "predict_match", lambda h, a, df: {"prediction": "home"})

    predict_ok = client.post("/fixtures/api/predict", json={"team_h_id": 1, "team_a_id": 2})
    assert predict_ok.status_code == 200
    assert predict_ok.get_json()["prediction"] == "home"

    same_team = client.post("/fixtures/api/predict", json={"team_h_id": 1, "team_a_id": 1})
    assert same_team.status_code == 400

    monkeypatch.setattr(fixtures_routes, "get_team_id_map", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    err = client.get("/fixtures/")
    assert err.status_code == 200


def test_help_routes_contact_validation_and_success(capsys):
    app = create_app()
    app.config.update(TESTING=True)
    client = app.test_client()

    page = client.get("/help/")
    assert page.status_code == 200

    missing = client.post("/help/contact", data={"name": "", "email": "", "subject": "", "message": ""})
    assert missing.status_code in (301, 302)

    invalid_email = client.post(
        "/help/contact",
        data={"name": "A", "email": "not-an-email", "subject": "S", "message": "M"},
    )
    assert invalid_email.status_code in (301, 302)

    success = client.post(
        "/help/contact",
        data={"name": "A", "email": "a@b.com", "subject": "S", "message": "M"},
    )
    assert success.status_code in (301, 302)

    out = capsys.readouterr().out
    assert "Contact form submission" in out


def test_create_routes_index_api_and_photo_map(monkeypatch):
    client = _client_logged_in()
    original_get_photo_map = create_routes._get_photo_map

    # Index path with loaded team list.
    df = pd.DataFrame(
        {
            "player_name": ["P1", "P2"],
            "team": ["Arsenal", "Chelsea"],
            "team_short": ["ARS", "CHE"],
            "position": ["MID", "FWD"],
            "minutes": [100, 200],
            "goals": [1, 2],
            "assists": [0, 1],
            "fpl_id": [11, 12],
        }
    )
    monkeypatch.setattr(create_routes, "_load_dataframe", lambda: df.copy())
    monkeypatch.setattr(create_routes, "_get_photo_map", lambda: ({11: "p1"}, {11: "b1"}))

    page = client.get("/create/")
    assert page.status_code == 200

    players = client.get("/create/api/players?position=MID&team=Arsenal&search=P")
    payload = players.get_json()
    assert players.status_code == 200
    assert len(payload["players"]) == 1

    # _get_photo_map success + failure branches.
    class _Resp:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "teams": [{"id": 1, "code": 3}],
                "elements": [{"id": 99, "team": 1, "photo": "111.jpg"}],
            }

    monkeypatch.setattr(create_routes.requests, "get", lambda *args, **kwargs: _Resp())
    photo_map, badge_map = original_get_photo_map()
    assert photo_map[99].endswith("p111.png")
    assert "premierleague/badges" in badge_map[99]

    monkeypatch.setattr(create_routes.requests, "get", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("no")))
    assert original_get_photo_map() == ({}, {})


def _leaderboard_df():
    return pd.DataFrame(
        {
            "player_name": ["A", "B", "C", "D"],
            "team_short": ["ARS", "CHE", "ARS", "CHE"],
            "position": ["MID", "MID", "GKP", "FWD"],
            "minutes": [900, 800, 900, 900],
            "goals": [10, 5, 0, 8],
            "xG": [8.0, 6.0, 0.2, 7.5],
            "now_cost": [10.0, 8.0, 5.0, 9.0],
            "total_points": [180, 120, 130, 150],
            "goals_p90": [1.0, 0.56, 0.0, 0.8],
            "xG_p90": [0.8, 0.67, 0.02, 0.75],
            "shots_p90": [3.0, 2.0, 0.1, 2.8],
            "assists_p90": [0.3, 0.2, 0.0, 0.1],
            "xA_p90": [0.25, 0.2, 0.0, 0.08],
            "key_passes_p90": [2.0, 1.5, 0.1, 1.1],
            "influence": [200, 150, 50, 180],
            "creativity": [210, 160, 40, 120],
            "threat": [220, 130, 20, 210],
            "ict_index": [300, 220, 70, 260],
        }
    )


def test_leaderboards_helpers_and_route(monkeypatch):
    client = create_app().test_client()

    monkeypatch.setattr(leaderboards_routes, "_load_master_df", lambda: _leaderboard_df())

    rows, metrics = leaderboards_routes._get_percentile_table()
    assert len(rows) > 0
    assert len(metrics) > 0

    value_data = leaderboards_routes._get_value_leaderboard()
    assert set(value_data.keys()) == {"GKP", "DEF", "MID", "FWD"}

    over, under = leaderboards_routes._get_xg_diff_leaderboard()
    assert len(over) > 0
    assert len(under) > 0

    class _FakeProcessor:
        def get_player_leaderboards(self):
            return {"goals": {"players": []}}

        def get_team_leaderboards(self):
            return {"goals": {"teams": []}}

    monkeypatch.setattr(leaderboards_routes, "LeaderboardsProcessor", lambda: _FakeProcessor())
    monkeypatch.setattr(leaderboards_routes, "get_current_user", lambda: None)

    for view in ["players", "teams", "percentiles", "value", "xg", "invalid"]:
        resp = client.get(f"/leaderboards/?view={view}")
        assert resp.status_code == 200
