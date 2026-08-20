"""Held-out evaluation, calibration, plotting, and MLflow report generation."""

from __future__ import annotations

import argparse
import json
from numbers import Real
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

from src.config import load_config
from src.evaluation.metrics import evaluate_with_macro_weighted, mcnemar_test, save_metric_result
from src.evaluation.plots import (
    plot_confusion,
    plot_reliability,
    plot_reliability_comparison,
    plot_roc_pr,
)
from src.tracking import experiment_run, log_artifact, log_metrics, log_parameters


class _ValidationCalibrator:
    """Calibrate a prefit binary estimator using validation scores only."""

    def __init__(self, estimator: Any, method: str) -> None:
        if method not in {"sigmoid", "isotonic"}:
            raise ValueError("method must be sigmoid or isotonic")
        self.estimator = estimator
        self.method = method

    def fit(self, X: Any, y: Any) -> _ValidationCalibrator:
        scores = np.asarray(self.estimator.predict_proba(X))[:, 1]
        target = np.asarray(y).astype(int)
        if self.method == "sigmoid":
            self.calibrator = LogisticRegression(max_iter=1000).fit(scores.reshape(-1, 1), target)
        else:
            self.calibrator = IsotonicRegression(out_of_bounds="clip").fit(scores, target)
        return self

    def predict_proba(self, X: Any) -> np.ndarray:
        scores = np.asarray(self.estimator.predict_proba(X))[:, 1]
        if self.method == "sigmoid":
            positive = self.calibrator.predict_proba(scores.reshape(-1, 1))[:, 1]
        else:
            positive = np.asarray(self.calibrator.predict(scores), dtype=float)
        positive = np.clip(positive, 0.0, 1.0)
        return np.column_stack([1.0 - positive, positive])


def _calibrate_prefit(artifact_model: Any, validation: pd.DataFrame, methods: tuple[str, ...]) -> tuple[dict[str, Any], Any]:
    """Fit Platt/isotonic maps on validation features only, then return test-time models."""
    estimator = getattr(artifact_model, "estimator", None)
    pipeline = getattr(artifact_model, "text_pipeline", None)
    if estimator is None or pipeline is None:
        raise TypeError("Calibration requires a PackagedTextModel with text_pipeline and estimator")
    X_validation = pipeline.transform(validation["content"].fillna("").tolist())
    y_validation = validation["label"].astype(int).to_numpy()
    calibrators: dict[str, Any] = {}
    for method in methods:
        calibrators[method] = _ValidationCalibrator(estimator, method).fit(X_validation, y_validation)
    return calibrators, pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a packaged fake-news model on held-out data")
    parser.add_argument("--test", default="data/processed/test.csv")
    parser.add_argument("--validation", default="data/processed/validation.csv")
    parser.add_argument("--artifact", default="artifacts/models/logistic_l2.joblib")
    parser.add_argument("--compare-artifact", default=None)
    parser.add_argument("--output", default="reports/evaluation/final_metrics.json")
    parser.add_argument("--report-dir", default="reports/evaluation")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--mlflow", action="store_true", help="Enable MLflow logging for this evaluation")
    parser.add_argument("--tracking-uri", default=None)
    parser.add_argument("--experiment-name", default=None)
    parser.add_argument("--artifact-location", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    tracking = config.values.get("tracking", {})
    tracking_enabled = bool(args.mlflow or tracking.get("enabled", False))
    tracking_uri = args.tracking_uri or str(tracking.get("uri", "mlruns"))
    experiment_name = args.experiment_name or str(tracking.get("experiment_name", "fake-news-detection"))
    artifact_location = args.artifact_location or tracking.get("artifact_location")
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    with experiment_run(enabled=tracking_enabled, tracking_uri=tracking_uri, experiment_name=experiment_name, artifact_location=artifact_location, run_name="held-out-evaluation") as run:
        test_frame = pd.read_csv(args.test)
        artifact = joblib.load(args.artifact)
        model = artifact["model"] if isinstance(artifact, dict) else artifact
        if not hasattr(model, "predict_proba"):
            raise TypeError("Packaged artifact must expose predict_proba")
        y_test = test_frame["label"].astype(int).to_numpy()
        test_probabilities = model.predict_proba(test_frame["content"].fillna("").tolist())
        result: dict[str, Any] = evaluate_with_macro_weighted(y_test, test_probabilities)
        result.update({"artifact": str(args.artifact), "test_rows": int(len(test_frame)), "final_test_evaluated_once": True, "test_data_used_for_selection": False})
        plot_confusion(y_test, (np.asarray(test_probabilities)[:, 1] >= 0.5).astype(int), report_dir / "confusion_matrix.png")
        plot_roc_pr(y_test, test_probabilities, report_dir / "roc_pr.png")
        plot_reliability(y_test, test_probabilities, report_dir / "reliability.png")

        probability_map: dict[str, Any] = {"uncalibrated": test_probabilities}
        validation_path = Path(args.validation)
        if validation_path.exists():
            validation_frame = pd.read_csv(validation_path)
            calibrators, pipeline = _calibrate_prefit(model, validation_frame, ("sigmoid", "isotonic"))
            calibration_results: dict[str, Any] = {}
            test_features = pipeline.transform(test_frame["content"].fillna("").tolist())
            for method, calibrator in calibrators.items():
                calibrated_probabilities = calibrator.predict_proba(test_features)
                probability_map[method] = calibrated_probabilities
                calibration_results[method] = evaluate_with_macro_weighted(y_test, calibrated_probabilities)
            result["calibration"] = calibration_results
            result["calibration_fit_split"] = "validation"
            plot_reliability_comparison(y_test, probability_map, report_dir / "calibration_comparison.png")
        else:
            result["calibration"] = {}
            result["calibration_fit_split"] = None

        if args.compare_artifact:
            comparison_artifact = joblib.load(args.compare_artifact)
            comparison_model = comparison_artifact["model"] if isinstance(comparison_artifact, dict) else comparison_artifact
            comparison_probabilities = comparison_model.predict_proba(test_frame["content"].fillna("").tolist())
            result["mcnemar"] = mcnemar_test(y_test, test_probabilities, comparison_probabilities)
            result["comparison_artifact"] = args.compare_artifact

        save_metric_result(result, args.output)
        log_parameters(run, {"test_rows": len(test_frame), "artifact": args.artifact, "validation": str(validation_path), "config": args.config, "final_test_evaluated_once": True})
        numeric_metrics = {key: float(value) for key, value in result.items() if isinstance(value, Real) and not isinstance(value, bool)}
        log_metrics(run, numeric_metrics)
        if tracking.get("log_config", True):
            log_artifact(run, args.config)
        log_artifact(run, args.output)
        log_artifact(run, report_dir / "confusion_matrix.png")
        log_artifact(run, report_dir / "roc_pr.png")
        log_artifact(run, report_dir / "reliability.png")
        if (report_dir / "calibration_comparison.png").exists():
            log_artifact(run, report_dir / "calibration_comparison.png")
    print(json.dumps(result, indent=2, default=float))


if __name__ == "__main__":
    main()
