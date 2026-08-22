from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from src.config import load_config
from src.evaluation.metrics import (
    calibrate_probabilities,
    evaluate_predictions,
    mcnemar_test,
    paired_bootstrap_regression,
    regression_metrics,
)
from src.evaluation.search import grid_search, search_result
from src.models.classical import (
    build_elasticnet_model,
    build_lasso_model,
    build_lightgbm,
    build_logistic_model,
    build_random_forest,
    build_ridge_model,
    build_xgboost,
    permutation_importance_table,
    shap_values,
)
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
    assert first["tracking_uri"].startswith("sqlite:///")
    assert first["artifact_location"].startswith("file://")
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


def test_phase3_linear_models_and_optional_boosting_configuration():
    X, y = fixture_matrix()
    for builder in (build_ridge_model, build_lasso_model, build_elasticnet_model):
        model = builder()
        model.fit(X, y.astype(float))
        assert model.predict(X).shape == (len(y),)
    pytest.importorskip("xgboost")
    xgb = build_xgboost(n_estimators=5, max_depth=2)
    assert xgb.get_params()["tree_method"] == "hist"
    pytest.importorskip("lightgbm")
    lgbm = build_lightgbm(n_estimators=5)
    assert lgbm.get_params()["boosting_type"] == "gbdt"


def test_search_result_and_train_only_search_contract():
    X, y = fixture_matrix()
    fitted = grid_search(build_logistic_model("l2", max_iter=200), {"classifier__C": [0.5, 1.0]}, X, y, cv_folds=2)
    result = search_result(fitted, "grid", 2, "average_precision", 42)
    assert result.test_data_used is False
    assert result.best_params
    assert result.trials is not None


def test_regression_metrics_and_paired_bootstrap_are_deterministic():
    actual = np.asarray([1.0, 2.0, 3.0, 4.0])
    prediction_a = np.asarray([1.1, 1.9, 3.2, 3.8])
    prediction_b = np.asarray([1.5, 2.5, 2.5, 3.5])
    metrics = regression_metrics(actual, prediction_a)
    assert set(metrics) == {"rmse", "mae", "mape", "r2"}
    first = paired_bootstrap_regression(actual, prediction_a, prediction_b, n_bootstrap=100, random_state=42)
    second = paired_bootstrap_regression(actual, prediction_a, prediction_b, n_bootstrap=100, random_state=42)
    assert first == second
    assert first["ci_low"] <= first["ci_high"]


def test_mcnemar_exact_probability_matches_paired_binomial():
    y = np.asarray([0, 0, 0, 0])
    model_a = np.asarray([[0.4, 0.6], [0.4, 0.6], [0.4, 0.6], [0.6, 0.4]])
    model_b = np.asarray([[0.6, 0.4], [0.6, 0.4], [0.6, 0.4], [0.4, 0.6]])
    result = mcnemar_test(y, model_a, model_b)
    assert result["discordant_pairs"] == 4
    assert result["exact_binomial_p_value"] == pytest.approx(0.625)


def test_validation_and_calibration_plot_artifacts(tmp_path):
    from src.evaluation.plots import plot_reliability_comparison, plot_validation_curve

    y = np.asarray([0, 1, 0, 1])
    probabilities = np.asarray([[0.8, 0.2], [0.2, 0.8], [0.7, 0.3], [0.3, 0.7]])
    assert plot_reliability_comparison(y, {"model": probabilities}, tmp_path / "reliability.png").exists()
    assert plot_validation_curve([1, 2], [[0.8, 0.9], [0.7, 0.8]], [[0.6, 0.7], [0.5, 0.6]], tmp_path / "validation.png").exists()


def test_nested_cv_search_uses_outer_training_fold_only():
    from src.evaluation.metrics import nested_stratified_cross_validate

    X, y = fixture_matrix()
    observed_sizes = []

    def factory(estimator, X_inner, y_inner, folds, seed):
        observed_sizes.append(len(y_inner))
        return grid_search(estimator, {"classifier__C": [0.5, 1.0]}, X_inner, y_inner, cv_folds=folds, random_state=seed)

    report = nested_stratified_cross_validate(
        build_logistic_model("l2", max_iter=200), factory, X, y, outer_folds=2, inner_folds=2
    )
    assert report["test_data_used_for_selection"] is False
    assert len(report["folds"]) == 2
    assert observed_sizes == [4, 4]
    assert report["mean_score"] >= 0.0


def test_tree_explainability_outputs_have_feature_schema():
    X, y = fixture_matrix()
    forest = build_random_forest(n_estimators=20, random_state=42).fit(X.toarray(), y)
    names = np.asarray(["f0", "f1", "f2"])
    permutation = permutation_importance_table(forest, X.toarray(), y, names, n_repeats=2)
    assert list(permutation.columns) == ["feature", "importance_mean", "importance_std"]
    pytest.importorskip("shap")
    shap_frame = shap_values(forest, X.toarray(), names, max_samples=8)
    assert list(shap_frame.columns) == ["feature", "mean_abs_shap"]
    assert len(shap_frame) == X.shape[1]
