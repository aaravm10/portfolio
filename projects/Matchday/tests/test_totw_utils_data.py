from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import totw
import utils.fixtures_data as fixtures_data
import utils.player_history as player_history


def _sample_bootstrap(current=True):
    return {
        "events": [
            {"id": 1, "is_current": False, "finished": True},
            {"id": 2, "is_current": current, "finished": not current},
            {"id": 3, "is_current": False, "finished": False},
        ],
        "teams": [
            {"id": 1, "name": "Arsenal", "short_name": "ARS", "code": 3},
            {"id": 2, "name": "Chelsea", "short_name": "CHE", "code": 8},
        ],
        "elements": [
            {
                "id": 11,
                "web_name": "Saka",
                "first_name": "Bukayo",
                "second_name": "Saka",
                "team": 1,
                "element_type": 3,
                "photo": "12345.jpg",
            },
            {
                "id": 12,
                "web_name": "Palmer",
                "first_name": "Cole",
                "second_name": "Palmer",
                "team": 2,
                "element_type": 3,
                "photo": "12346.png",
            },
        ],
    }


def _sample_gw_live():
    return {
        "elements": [
            {
                "id": 11,
                "stats": {
                    "minutes": 90,
                    "goals_scored": 1,
                    "assists": 0,
                    "clean_sheets": 0,
                    "goals_conceded": 0,
                    "saves": 0,
                    "yellow_cards": 0,
                    "red_cards": 0,
                    "bonus": 2,
                    "bps": 20,
                    "influence": "30.0",
                    "creativity": "25.0",
                    "threat": "50.0",
                    "ict_index": "10.5",
                },
            },
            {
                "id": 12,
                "stats": {
                    "minutes": 0,
                    "goals_scored": 0,
                    "assists": 0,
                    "clean_sheets": 0,
                    "goals_conceded": 0,
                    "saves": 0,
                    "yellow_cards": 0,
                    "red_cards": 0,
                    "bonus": 0,
                    "bps": 0,
                    "influence": "0.0",
                    "creativity": "0.0",
                    "threat": "0.0",
                    "ict_index": "0.0",
                },
            },
        ]
    }


class TestTotwCore:
    def test_get_current_gameweek_prefers_current(self, monkeypatch):
        fetcher = totw.GameweekFetcher()
        monkeypatch.setattr(fetcher, "get_bootstrap_data", lambda: _sample_bootstrap(current=True))
        assert fetcher.get_current_gameweek() == 2

    def test_get_current_gameweek_falls_back_to_finished(self, monkeypatch):
        fetcher = totw.GameweekFetcher()
        monkeypatch.setattr(fetcher, "get_bootstrap_data", lambda: _sample_bootstrap(current=False))
        assert fetcher.get_current_gameweek() == 2

    def test_data_processor_builds_dataframe_and_filters_zero_minutes(self, monkeypatch):
        processor = totw.DataProcessor()
        monkeypatch.setattr(processor.fetcher, "get_bootstrap_data", lambda: _sample_bootstrap(current=True))
        monkeypatch.setattr(processor.fetcher, "get_gameweek_data", lambda gw: _sample_gw_live())

        df = processor.build_gameweek_dataframe(2)

        assert len(df) == 1
        assert df.iloc[0]["player_name"] == "Saka"
        assert df.iloc[0]["team_short"] == "ARS"

    def test_totw_scorer_minutes_penalty_applies(self):
        scorer = totw.TOTWScorer()
        df = pd.DataFrame(
            {
                "player_name": ["A", "B"],
                "position": [3, 3],
                "minutes": [50, 90],
                "goals": [1, 1],
                "assists": [0, 0],
                "clean_sheets": [0, 0],
                "goals_conceded": [0, 0],
                "saves": [0, 0],
                "yellow_cards": [0, 0],
                "red_cards": [0, 0],
                "bonus": [0, 0],
                "bps": [0, 0],
                "influence": [10.0, 10.0],
                "creativity": [10.0, 10.0],
                "threat": [10.0, 10.0],
                "ict_index": [0.0, 0.0],
            }
        )

        scored = scorer.calculate_scores(df)
        assert scored.loc[0, "totw_score"] < scored.loc[1, "totw_score"]

    def test_totw_rating_handles_empty_non_positive_and_outlier(self):
        scorer = totw.TOTWScorer()

        empty = scorer.calculate_rating(pd.DataFrame())
        assert empty.empty

        non_positive = scorer.calculate_rating(pd.DataFrame({"totw_score": [-1.0, 0.0]}))
        assert set(non_positive["rating"].tolist()) == {8.0}

        # Outlier with hat-trick should be promoted to 10.0
        outlier_df = pd.DataFrame(
            {
                "totw_score": [40.0, 20.0],
                "goals": [3, 1],
                "assists": [0, 0],
            }
        )
        rated = scorer.calculate_rating(outlier_df)
        assert rated["rating"].max() == 10.0

    def test_formation_selector_fixed_and_dynamic_paths(self):
        selector = totw.FormationSelector()
        # Enough players for dynamic choice
        df = pd.DataFrame(
            {
                "player_name": [f"P{i}" for i in range(1, 17)],
                "position": [1] + [2] * 5 + [3] * 5 + [4] * 5,
                "totw_score": list(range(16, 0, -1)),
            }
        )

        fixed = selector.select_best_xi(df, "4-3-3")
        assert len(fixed) == 11

        dynamic, formation = selector.select_best_xi_dynamic(df)
        assert len(dynamic) == 11
        assert formation in {"3-4-3", "3-5-2", "4-3-3", "4-4-2", "4-5-1", "5-3-2", "5-4-1"}

        # Fallback path: not enough defenders/midfielders/forwards for dynamic loop.
        tiny = pd.DataFrame(
            {
                "player_name": ["GK", "D1", "M1", "F1"],
                "position": [1, 2, 3, 4],
                "totw_score": [10, 9, 8, 7],
            }
        )
        fallback, fallback_form = selector.select_best_xi_dynamic(tiny)
        assert fallback_form == "4-3-3"
        assert len(fallback) == 4


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


class TestFixturesData:
    def setup_method(self):
        fixtures_data._BOOTSTRAP_CACHE["ts"] = 0
        fixtures_data._BOOTSTRAP_CACHE["data"] = None
        fixtures_data._FIXTURES_CACHE["ts"] = 0
        fixtures_data._FIXTURES_CACHE["data"] = None

    def test_fetch_functions_use_cache(self, monkeypatch):
        calls = {"bootstrap": 0, "fixtures": 0}

        def _fake_get(url, timeout):
            if "bootstrap-static" in url:
                calls["bootstrap"] += 1
                return _Resp(_sample_bootstrap(current=True))
            calls["fixtures"] += 1
            return _Resp([{"event": 1}])

        monkeypatch.setattr(fixtures_data.requests, "get", _fake_get)

        b1 = fixtures_data._fetch_bootstrap()
        b2 = fixtures_data._fetch_bootstrap()
        f1 = fixtures_data._fetch_raw_fixtures()
        f2 = fixtures_data._fetch_raw_fixtures()

        assert b1 == b2
        assert f1 == f2
        assert calls["bootstrap"] == 1
        assert calls["fixtures"] == 1

    def test_team_map_current_gameweek_and_fdr_matrix(self, monkeypatch):
        monkeypatch.setattr(fixtures_data, "_fetch_bootstrap", lambda: _sample_bootstrap(current=True))
        monkeypatch.setattr(
            fixtures_data,
            "_fetch_raw_fixtures",
            lambda: [
                {
                    "finished": False,
                    "event": 2,
                    "team_h": 1,
                    "team_a": 2,
                    "team_h_difficulty": 2,
                    "team_a_difficulty": 4,
                },
                {
                    "finished": True,
                    "event": 1,
                    "team_h": 1,
                    "team_a": 2,
                    "team_h_difficulty": 3,
                    "team_a_difficulty": 3,
                },
            ],
        )

        team_map = fixtures_data.get_team_id_map()
        assert team_map[1]["short_name"] == "ARS"

        current_gw = fixtures_data.get_current_gameweek()
        assert current_gw == 2

        matrix = fixtures_data.get_fdr_matrix(n_upcoming=2)
        assert matrix[1][0]["opponent_short"] == "CHE"
        assert matrix[1][0]["difficulty"] == 2

    def test_predict_match_handles_branches(self):
        df = pd.DataFrame(
            {
                "team": ["Arsenal", "Arsenal", "Chelsea", "Chelsea"],
                "position": ["MID", "GKP", "MID", "GKP"],
                "xG": [20.0, 0.0, 10.0, 0.0],
                "games": [10, 10, 10, 10],
                "goals_conceded": [0, 8, 0, 12],
            }
        )

        def _team_map():
            return {
                1: {"name": "Arsenal", "short_name": "ARS", "code": 3, "badge_url": "x"},
                2: {"name": "Chelsea", "short_name": "CHE", "code": 8, "badge_url": "y"},
            }

        fixtures_data.get_team_id_map = _team_map

        result = fixtures_data.predict_match(1, 2, df)
        assert result["prediction"] in {"home", "away", "draw"}
        assert result["confidence"] in {"low", "medium", "high"}

        assert "error" in fixtures_data.predict_match(1, 2, pd.DataFrame())


class TestPlayerHistory:
    def setup_method(self):
        player_history._HISTORY_CACHE.clear()

    def test_fetch_player_history_success_and_cache(self, monkeypatch):
        calls = {"n": 0}

        def _fake_get(url, timeout):
            calls["n"] += 1
            return _Resp({"history": [{"round": 1, "minutes": 90}]})

        monkeypatch.setattr(player_history.requests, "get", _fake_get)

        h1 = player_history.fetch_player_history(99)
        h2 = player_history.fetch_player_history(99)

        assert h1 == h2
        assert calls["n"] == 1

    def test_fetch_player_history_failure_returns_empty(self, monkeypatch):
        def _boom(url, timeout):
            raise RuntimeError("network")

        monkeypatch.setattr(player_history.requests, "get", _boom)
        assert player_history.fetch_player_history(9) == []

    def test_form_stats_and_timeline(self):
        history = [
            {"round": 1, "minutes": 90, "goals_scored": 1, "assists": 0, "total_points": 7, "clean_sheets": 0},
            {"round": 2, "minutes": 45, "goals_scored": 0, "assists": 1, "total_points": 5, "clean_sheets": 0},
            {"round": 3, "minutes": 0, "goals_scored": 0, "assists": 0, "total_points": 0, "clean_sheets": 0},
        ]

        form = player_history.get_form_stats(history, n_gw=2)
        assert len(form["gws"]) == 2
        assert form["avg_points"] == 6.0

        timeline = player_history.get_cumulative_timeline(history)
        assert timeline[-1]["cumulative_points"] == 12
        assert player_history.get_form_stats([], n_gw=5)["gws"] == []
