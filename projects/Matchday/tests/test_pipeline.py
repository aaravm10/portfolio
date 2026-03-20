from pathlib import Path
import copy
import sys

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline import DataFrameBuilder, MasterPipeline, PipelineUtils, write_excel


@pytest.fixture()
def sample_fpl_bootstrap():
    return {
        "elements": [
            {
                "id": 1,
                "first_name": "Bukayo",
                "second_name": "Saka",
                "web_name": "Saka",
                "team": 1,
                "element_type": 3,
                "minutes": "900",
                "starts": "10",
                "goals_scored": "5",
                "assists": "3",
                "clean_sheets": "0",
                "goals_conceded": "0",
                "saves": "0",
                "yellow_cards": "2",
                "red_cards": "0",
                "influence": "100",
                "creativity": "200",
                "threat": "300",
                "ict_index": "400",
            },
            {
                "id": 2,
                "first_name": "Erling",
                "second_name": "Haaland",
                "web_name": "Haaland",
                "team": 2,
                "element_type": 4,
                "minutes": "800",
                "starts": "9",
                "goals_scored": "8",
                "assists": "1",
                "clean_sheets": "0",
                "goals_conceded": "0",
                "saves": "0",
                "yellow_cards": "1",
                "red_cards": "0",
                "influence": "110",
                "creativity": "120",
                "threat": "500",
                "ict_index": "510",
            },
        ],
        "teams": [
            {"id": 1, "name": "Arsenal", "short_name": "ARS"},
            {"id": 2, "name": "Man City", "short_name": "MCI"},
        ],
        "element_types": [
            {"id": 3, "singular_name_short": "MID"},
            {"id": 4, "singular_name_short": "FWD"},
        ],
    }


@pytest.fixture()
def sample_understat_players():
    return [
        {
            "id": "101",
            "player_name": "Bukayo Saka",
            "team_title": "Arsenal",
            "position": "MID",
            "games": "10",
            "time": "900",
            "goals": "5",
            "xG": "4.2",
            "assists": "3",
            "xA": "2.1",
            "shots": "20",
            "key_passes": "15",
            "yellow_cards": "2",
            "red_cards": "0",
            "npg": "5",
            "npxG": "4.1",
            "xGChain": "8.0",
            "xGBuildup": "2.2",
        }
    ]


def clone_fpl_bootstrap(sample_fpl_bootstrap):
    return copy.deepcopy(sample_fpl_bootstrap)


def clone_understat_players(sample_understat_players):
    return copy.deepcopy(sample_understat_players)


class TestPipelineUtils:
    def test_norm_text_basic(self):
        assert PipelineUtils.norm_text(" Éléphant- FC  ") == "elephantfc"

    def test_norm_text_none(self):
        assert PipelineUtils.norm_text(None) == ""

    def test_to_num_coerces(self):
        df = pd.DataFrame({"a": ["1", "x"], "b": [2, "3"]})
        PipelineUtils.to_num(df, ["a", "b", "c"])
        assert pd.isna(df.loc[1, "a"])
        assert df.loc[0, "a"] == 1
        assert df.loc[1, "b"] == 3

    def test_per90_handles_zero(self):
        series = pd.Series([10, 5])
        minutes = pd.Series([90, 0])
        result = PipelineUtils.per90(series, minutes)
        assert result.loc[0] == 10
        assert pd.isna(result.loc[1])

    def test_coalesce_prefers_primary(self):
        primary = pd.Series([1, None, 3])
        secondary = pd.Series([10, 20, 30])
        result = PipelineUtils.coalesce(primary, secondary)
        assert result.tolist() == [1, 20, 3]


class TestDataFrameBuilder:
    def test_build_fpl_df_columns(self, sample_fpl_bootstrap):
        fpl = DataFrameBuilder.build_fpl_df(sample_fpl_bootstrap)
        assert "player_key" in fpl.columns
        assert "team_key" in fpl.columns
        assert "FPL_minutes" in fpl.columns
        assert "FPL_player_name" in fpl.columns

    def test_build_fpl_df_values(self, sample_fpl_bootstrap):
        fpl = DataFrameBuilder.build_fpl_df(sample_fpl_bootstrap)
        assert fpl.loc[0, "player_key"] == "bukayosaka"
        assert fpl.loc[0, "team_key"] == "arsenal"
        assert fpl.loc[0, "FPL_minutes"] == 900

    def test_build_fpl_df_numeric_types(self, sample_fpl_bootstrap):
        fpl = DataFrameBuilder.build_fpl_df(sample_fpl_bootstrap)
        assert pd.api.types.is_numeric_dtype(fpl["FPL_minutes"])
        assert pd.api.types.is_numeric_dtype(fpl["FPL_goals_scored"])

    def test_build_understat_df_columns(self, sample_understat_players):
        us = DataFrameBuilder.build_understat_df(sample_understat_players)
        assert "player_key" in us.columns
        assert "team_key_raw" in us.columns
        assert "time" in us.columns

    def test_build_understat_df_numeric_types(self, sample_understat_players):
        us = DataFrameBuilder.build_understat_df(sample_understat_players)
        assert pd.api.types.is_numeric_dtype(us["time"])
        assert pd.api.types.is_numeric_dtype(us["xG"])


class TestTeamMapping:
    def test_map_understat_teams_exact_match(self):
        us = pd.DataFrame({"team_key_raw": ["mancity"]})
        fpl = pd.DataFrame({"team_key": ["mancity"]})
        mapped, _ = DataFrameBuilder.map_understat_teams_to_fpl(us, fpl)
        assert mapped.loc[0, "team_key"] == "mancity"

    def test_map_understat_teams_fuzzy_match(self):
        us = pd.DataFrame({"team_key_raw": ["manchestercity"]})
        fpl = pd.DataFrame({"team_key": ["mancity"]})
        mapped, _ = DataFrameBuilder.map_understat_teams_to_fpl(us, fpl)
        assert mapped.loc[0, "team_key"] == "mancity"

    def test_map_understat_teams_keeps_unknown(self):
        us = pd.DataFrame({"team_key_raw": ["unknownfc"]})
        fpl = pd.DataFrame({"team_key": ["mancity"]})
        mapped, _ = DataFrameBuilder.map_understat_teams_to_fpl(us, fpl)
        assert mapped.loc[0, "team_key"] == "unknownfc"

    def test_map_understat_teams_returns_map_df(self):
        us = pd.DataFrame({"team_key_raw": ["mancity", "manchestercity"]})
        fpl = pd.DataFrame({"team_key": ["mancity"]})
        _, map_df = DataFrameBuilder.map_understat_teams_to_fpl(us, fpl)
        assert "understat_team_key" in map_df.columns
        assert "mapped_fpl_team_key" in map_df.columns
        assert len(map_df) == 2

    def test_map_understat_teams_does_not_mutate_input(self):
        us = pd.DataFrame({"team_key_raw": ["mancity"]})
        fpl = pd.DataFrame({"team_key": ["mancity"]})
        original = us.copy()
        DataFrameBuilder.map_understat_teams_to_fpl(us, fpl)
        assert "team_key" not in original.columns
        assert list(us.columns) == list(original.columns)


class TestMasterPipeline:
    def _patch_fetchers(self, monkeypatch, fpl_data, us_data):
        monkeypatch.setattr(
            "pipeline.DataFetcher.fetch_fpl_bootstrap",
            lambda: fpl_data,
        )
        monkeypatch.setattr(
            "pipeline.DataFetcher.fetch_understat_league_players",
            lambda season: us_data,
        )

    def test_build_master_returns_frames(self, monkeypatch, sample_fpl_bootstrap, sample_understat_players):
        self._patch_fetchers(monkeypatch, sample_fpl_bootstrap, sample_understat_players)
        frames = MasterPipeline.build_master(season=2024)
        assert "master" in frames
        assert "raw" in frames
        assert "understat_only" in frames
        assert "unmatched_fpl" in frames
        assert "team_mapping" in frames

    def test_build_master_merge_status(self, monkeypatch, sample_fpl_bootstrap, sample_understat_players):
        self._patch_fetchers(monkeypatch, sample_fpl_bootstrap, sample_understat_players)
        frames = MasterPipeline.build_master(season=2024)
        master = frames["master"]
        saka = master[master["player_name"] == "Bukayo Saka"].iloc[0]
        haaland = master[master["player_name"] == "Erling Haaland"].iloc[0]
        assert saka["merge_status"] == "matched"
        assert haaland["merge_status"] == "no_understat_match"

    def test_build_master_p90_calculated(self, monkeypatch, sample_fpl_bootstrap, sample_understat_players):
        self._patch_fetchers(monkeypatch, sample_fpl_bootstrap, sample_understat_players)
        frames = MasterPipeline.build_master(season=2024)
        master = frames["master"]
        saka = master[master["player_name"] == "Bukayo Saka"].iloc[0]
        assert saka["goals_p90"] == pytest.approx(0.5)

    def test_build_master_prefer_fpl_for(self, monkeypatch, sample_fpl_bootstrap, sample_understat_players):
        fpl_data = clone_fpl_bootstrap(sample_fpl_bootstrap)
        us_data = clone_understat_players(sample_understat_players)
        fpl_data["elements"][0]["goals_scored"] = "7"
        self._patch_fetchers(monkeypatch, fpl_data, us_data)
        frames = MasterPipeline.build_master(season=2024, prefer_fpl_for={"goals"})
        master = frames["master"]
        saka = master[master["player_name"] == "Bukayo Saka"].iloc[0]
        assert saka["goals"] == 7

    def test_build_master_prefer_understat_for(self, monkeypatch, sample_fpl_bootstrap, sample_understat_players):
        fpl_data = clone_fpl_bootstrap(sample_fpl_bootstrap)
        us_data = clone_understat_players(sample_understat_players)
        fpl_data["elements"][0]["goals_scored"] = "7"
        self._patch_fetchers(monkeypatch, fpl_data, us_data)
        frames = MasterPipeline.build_master(season=2024, prefer_fpl_for=set())
        master = frames["master"]
        saka = master[master["player_name"] == "Bukayo Saka"].iloc[0]
        assert saka["goals"] == 5


class TestWriteExcel:
    def test_write_excel_creates_file(self, tmp_path):
        frames = {
            "master": pd.DataFrame({"a": [1]}),
            "raw": pd.DataFrame({"a": [1]}),
            "unmatched_fpl": pd.DataFrame({"a": [1]}),
            "understat_only": pd.DataFrame({"a": [1]}),
            "team_mapping": pd.DataFrame({"a": [1]}),
        }
        path = tmp_path / "out.xlsx"
        result = write_excel(frames, path)
        assert Path(result).exists()

    def test_write_excel_sheet_names(self, tmp_path):
        frames = {
            "master": pd.DataFrame({"a": [1]}),
            "raw": pd.DataFrame({"a": [1]}),
            "unmatched_fpl": pd.DataFrame({"a": [1]}),
            "understat_only": pd.DataFrame({"a": [1]}),
            "team_mapping": pd.DataFrame({"a": [1]}),
        }
        path = tmp_path / "out.xlsx"
        result = write_excel(frames, path)
        xls = pd.ExcelFile(result)
        assert set(xls.sheet_names) == {
            "MASTER",
            "RAW_MERGED",
            "UNMATCHED_FPL",
            "UNDERSTAT_ONLY",
            "TEAM_MAPPING",
        }

    def test_write_excel_returns_string(self, tmp_path):
        frames = {
            "master": pd.DataFrame({"a": [1]}),
            "raw": pd.DataFrame({"a": [1]}),
            "unmatched_fpl": pd.DataFrame({"a": [1]}),
            "understat_only": pd.DataFrame({"a": [1]}),
            "team_mapping": pd.DataFrame({"a": [1]}),
        }
        path = tmp_path / "out.xlsx"
        result = write_excel(frames, path)
        assert isinstance(result, str)

    def test_write_excel_accepts_pathlike(self, tmp_path):
        frames = {
            "master": pd.DataFrame({"a": [1]}),
            "raw": pd.DataFrame({"a": [1]}),
            "unmatched_fpl": pd.DataFrame({"a": [1]}),
            "understat_only": pd.DataFrame({"a": [1]}),
            "team_mapping": pd.DataFrame({"a": [1]}),
        }
        path = tmp_path / "out.xlsx"
        result = write_excel(frames, Path(path))
        assert Path(result).exists()

    def test_write_excel_overwrites(self, tmp_path):
        frames = {
            "master": pd.DataFrame({"a": [1]}),
            "raw": pd.DataFrame({"a": [1]}),
            "unmatched_fpl": pd.DataFrame({"a": [1]}),
            "understat_only": pd.DataFrame({"a": [1]}),
            "team_mapping": pd.DataFrame({"a": [1]}),
        }
        path = tmp_path / "out.xlsx"
        write_excel(frames, path)
        result = write_excel(frames, path)
        assert Path(result).exists()
