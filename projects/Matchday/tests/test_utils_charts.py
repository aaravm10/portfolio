from pathlib import Path
import sys

import matplotlib
import pandas as pd

matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import utils.charts as charts


def test_file_mtime_returns_zero_for_missing(tmp_path):
    assert charts.file_mtime(tmp_path / "does-not-exist") == 0


def test_file_mtime_returns_stat_time(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("hello")
    assert charts.file_mtime(f) > 0


def test_load_master_xlsx_delegates_to_pandas(monkeypatch):
    captured = {}

    def _fake_read_excel(path, sheet_name):
        captured["path"] = path
        captured["sheet_name"] = sheet_name
        return pd.DataFrame({"a": [1]})

    monkeypatch.setattr(charts.pd, "read_excel", _fake_read_excel)

    df = charts.load_master_xlsx("dummy.xlsx", 123)

    assert isinstance(df, pd.DataFrame)
    assert captured == {"path": "dummy.xlsx", "sheet_name": "MASTER"}


def test_compute_percentiles_global_and_grouped():
    df = pd.DataFrame(
        {
            "team": ["A", "A", "B", "B"],
            "metric": [1, 2, 2, 4],
        }
    )

    global_df = charts.compute_percentiles(df, ["metric", "missing"])
    grouped_df = charts.compute_percentiles(df, ["metric"], group_col="team")

    assert "metric_pct" in global_df.columns
    assert grouped_df.loc[1, "metric_pct"] == 100.0


def test_draw_radial_build_and_base64_roundtrip():
    labels = ["A", "B", "C", "D"]
    values = [0.8, 0.0, 0.35, 1.0]
    colors = ["#111111", "#222222", "#333333", "#444444"]

    fig = charts.build_radial_figure(labels, values, colors, group_bounds=[0, 2, 99])
    encoded = charts.figure_to_base64(fig)

    assert isinstance(encoded, str)
    assert len(encoded) > 20


def test_get_3d_model_base64_both_paths(tmp_path):
    missing = charts.get_3d_model_base64(tmp_path / "missing.glb")

    model = tmp_path / "ball.glb"
    model.write_bytes(b"binary-model")
    present = charts.get_3d_model_base64(model)

    assert missing == ""
    assert isinstance(present, str)
    assert len(present) > 0
