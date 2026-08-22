"""Create a deterministic local MLflow run used to validate report generation in CI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tracking import initialize_tracking


def create_fixture_run(tracking_uri: str, experiment_name: str, fixture_path: str | Path) -> dict[str, str]:
    """Persist a small non-content fixture run using the MLflow 3-compatible local backend."""
    import mlflow

    tracking = initialize_tracking(tracking_uri=tracking_uri, experiment_name=experiment_name)
    fixture = Path(fixture_path)
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text(
        json.dumps({"status": "fixture", "test_data_used_for_selection": False}),
        encoding="utf-8",
    )
    mlflow.set_tracking_uri(tracking["tracking_uri"])
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run(run_name="fixture-report") as run:
        mlflow.log_metric("pr_auc", 1.0)
        mlflow.log_param("model", "fixture-logistic-l2")
        mlflow.log_param("test_data_used_for_selection", "false")
        mlflow.log_artifact(str(fixture))
    return {"tracking_uri": tracking["tracking_uri"], "run_id": run.info.run_id}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a deterministic local MLflow report fixture")
    parser.add_argument("--tracking-uri", required=True)
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--fixture-path", required=True)
    args = parser.parse_args()
    print(json.dumps(create_fixture_run(args.tracking_uri, args.experiment_name, args.fixture_path)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
