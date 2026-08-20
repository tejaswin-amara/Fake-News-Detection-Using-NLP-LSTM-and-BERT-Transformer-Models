from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from src.config import load_config
from src.evaluation.metrics import calibrate_probabilities, evaluate_predictions, mcnemar_test
from src.models.classical import build_logistic_model, build_random_forest
from src.models.unsupervised import UnsupervisedAnalyzer
from src.monitoring.drift import monitor_features, population_stability_index
from src.tracking import initialize_tracking


def fixture_matrix():
    X = np.asarray(
        [
            [1.0, 0.0, 0.1],
            [0.0, 1.0, 0.2],
            [1.0, 0.1, 0.0],
            [0.1, 1.0, 0.1],
            [1.0, 0.2, 0.0],
            [0.0, 1.0, 0.3],
            [0.9, 0.0, 0.1],
            [0.0, 0.9, 0.2],
        ]
    )
    y = np.asarray([0, 1, 0, 1, 0, 1, 0, 1])
    return sparse.csr_matrix(X), y


def test_logistic_and_random_forest_train():
    X, y = fixture_matrix()
    logistic = build_logistic_model("l2", max_iter=100)
    logistic.fit(X, y)
    assert logistic.predict_proba(X).shape == (len(y), 2)
    forest = build_random_forest(n_estimators=10)
    forest.fit(X.toarray(), y)
    assert forest.oob_score_ >= 0.0


def test_configuration_uses_required_bert_identifier():
    config = load_config("configs/default.yaml")
    assert config.values["models"]["bert"]["model_name"] == "bert-base-uncased"
    assert config.values["text"]["transformer"]["model_name"] == "bert-base-uncased"


def test_configuration_includes_dvc_and_tracking_flags():
    config = load_config("configs/default.yaml")
    assert config.values["dvc"]["pipeline_file"] == "dvc.yaml"
    assert config.values["dvc"]["cache_dir"] == ".dvc/cache"
    assert config.values["tracking"]["enabled"] is False
    assert config.values["tracking"]["experiment_name"] == "fake-news-detection"


def test_local_mlflow_initialization_is_idempotent(tmp_path):
    pytest.importorskip("mlflow")
    first = initialize_tracking(
        tracking_uri=str(tmp_path / "mlruns"),
        experiment_name="fixture-experiment",
    )
    second = initialize_tracking(
        tracking_uri=str(tmp_path / "mlruns"),
        experiment_name="fixture-experiment",
    )
    assert first["experiment_id"] == second["experiment_id"]
    assert first["experiment_name"] == "fixture-experiment"


def test_metrics_and_mcnemar_are_structured():
    y = np.asarray([0, 1, 0, 1])
    proba_a = np.asarray([[0.8, 0.2], [0.2, 0.8], [0.7, 0.3], [0.2, 0.8]])
    proba_b = np.asarray([[0.6, 0.4], [0.4, 0.6], [0.3, 0.7], [0.2, 0.8]])
    result = evaluate_predictions(y, proba_a)
    assert result.accuracy == 1.0
    comparison = mcnemar_test(y, proba_a, proba_b)
    assert "p_value" in comparison
    assert "exact_binomial_p_value" in comparison
    assert 0.0 <= comparison["exact_binomial_p_value"] <= 1.0
    assert comparison["discordant_pairs"] >= 0


def test_calibration_returns_two_probability_matrices():
    X, y = fixture_matrix()
    estimator = build_logistic_model("l2", max_iter=100)
    calibrated = calibrate_probabilities(estimator, X, y, X, methods=("sigmoid", "isotonic"), cv=2)
    assert set(calibrated) == {"sigmoid", "isotonic"}
    assert calibrated["sigmoid"].shape == (len(y), 2)


def test_unsupervised_fit_and_feature_labels():
    X, _ = fixture_matrix()
    analyzer = UnsupervisedAnalyzer()
    diagnostics = analyzer.kmeans_diagnostics(X, [2, 3])
    assert len(diagnostics.inertias) == 2
    analyzer.fit_kmeans(X, 2).fit_isolation_forest(X)
    labels = analyzer.labels(X)
    assert "kmeans_label" in labels
    assert "anomaly_score" in labels


def test_drift_monitoring_detects_shift():
    reference = {"f1": np.linspace(0, 1, 100), "f2": np.linspace(1, 2, 100)}
    current = {"f1": np.linspace(0.8, 1.8, 100), "f2": np.linspace(1, 2, 100)}
    report = monitor_features(reference, current, psi_threshold=0.05)
    assert report["features"]["f1"]["psi"] > 0.0
    assert report["drift_detected"] is True
    assert population_stability_index(reference["f2"], current["f2"]) == 0.0
