"""Held-out evaluation entry point with optional MLflow logging."""

from __future__ import annotations

import argparse
import json
from numbers import Real

import joblib
import pandas as pd

from src.config import load_config
from src.evaluation.metrics import evaluate_with_macro_weighted, save_metric_result
from src.tracking import experiment_run, log_artifact, log_metrics, log_parameters


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a packaged fake-news model")
    parser.add_argument("--test", default="data/processed/test.csv")
    parser.add_argument("--artifact", default="artifacts/models/logistic_l2.joblib")
    parser.add_argument("--output", default="reports/evaluation.json")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--mlflow", action="store_true", help="Enable MLflow logging for this run")
    parser.add_argument("--tracking-uri", default=None)
    parser.add_argument("--experiment-name", default=None)
    parser.add_argument("--artifact-location", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    tracking = config.values.get("tracking", {})
    tracking_enabled = bool(args.mlflow or tracking.get("enabled", False))
    tracking_uri = args.tracking_uri or str(tracking.get("uri", "mlruns"))
    experiment_name = args.experiment_name or str(
        tracking.get("experiment_name", "fake-news-detection")
    )
    artifact_location = args.artifact_location or tracking.get("artifact_location")

    with experiment_run(
        enabled=tracking_enabled,
        tracking_uri=tracking_uri,
        experiment_name=experiment_name,
        artifact_location=artifact_location,
        run_name="held-out-evaluation",
    ) as run:
        frame = pd.read_csv(args.test)
        artifact = joblib.load(args.artifact)
        model = artifact["model"] if isinstance(artifact, dict) else artifact
        if not hasattr(model, "predict_proba"):
            raise TypeError("Packaged artifact must expose predict_proba")
        probabilities = model.predict_proba(frame["content"].fillna("").tolist())
        result = evaluate_with_macro_weighted(
            frame["label"].astype(int).to_numpy(), probabilities
        )
        result["artifact"] = str(args.artifact)
        result["test_rows"] = int(len(frame))
        save_metric_result(result, args.output)
        log_parameters(
            run,
            {
                "test_rows": len(frame),
                "artifact": args.artifact,
                "config": args.config,
            },
        )
        numeric_metrics = {
            key: float(value)
            for key, value in result.items()
            if isinstance(value, Real) and not isinstance(value, bool)
        }
        log_metrics(run, numeric_metrics)
        if tracking.get("log_config", True):
            log_artifact(run, args.config)
        log_artifact(run, args.output)
        log_artifact(run, args.artifact)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
