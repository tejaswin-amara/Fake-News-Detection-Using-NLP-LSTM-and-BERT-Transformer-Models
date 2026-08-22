"""Regression coverage for the SQLite-backed MLflow report fixture helper."""

from __future__ import annotations

import pytest

from scripts.create_mlflow_report_fixture import create_fixture_run


def test_create_fixture_run_uses_sqlite_tracking_and_logs_a_fixture(tmp_path) -> None:
    """Keep CI report fixtures out of MLflow's deprecated filesystem metadata store."""
    pytest.importorskip("mlflow")
    result = create_fixture_run(
        tracking_uri=str(tmp_path / "tracking"),
        experiment_name="report-fixture-test",
        fixture_path=tmp_path / "fixture.json",
    )
    assert result["tracking_uri"].startswith("sqlite:///")
    assert result["run_id"]
    assert (tmp_path / "fixture.json").is_file()
