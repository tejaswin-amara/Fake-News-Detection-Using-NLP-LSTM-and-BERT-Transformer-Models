"""Evaluation, calibration, model selection, and statistical testing.

Compliant with M5/CO5. References SRC-024, SRC-025, SRC-026, SRC-027, SRC-028,
and SRC-029 in docs/sources.md.
The module accepts predictions from any model family through a common probability
array contract and never fits calibration on the final test set.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate


@dataclass
class MetricResult:
    accuracy: float
    precision: float
    recall: float
    f1_macro: float
    f1_weighted: float
    roc_auc: float | None
    pr_auc: float | None
    brier_score: float | None
    confusion_matrix: list[list[int]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_predictions(y_true: Any, probabilities: Any, threshold: float = 0.5) -> MetricResult:
    y = np.asarray(y_true).astype(int)
    proba = np.asarray(probabilities)
    positive = proba[:, 1] if proba.ndim == 2 else proba.reshape(-1)
    predicted = (positive >= threshold).astype(int)
    try:
        roc_auc: float | None = float(roc_auc_score(y, positive))
    except ValueError:
        roc_auc = None
    try:
        pr_auc: float | None = float(average_precision_score(y, positive))
    except ValueError:
        pr_auc = None
    return MetricResult(
        accuracy=float(accuracy_score(y, predicted)),
        precision=float(precision_score(y, predicted, zero_division=0)),
        recall=float(recall_score(y, predicted, zero_division=0)),
        f1_macro=float(f1_score(y, predicted, average="macro", zero_division=0)),
        f1_weighted=float(f1_score(y, predicted, average="weighted", zero_division=0)),
        roc_auc=roc_auc,
        pr_auc=pr_auc,
        brier_score=float(brier_score_loss(y, positive)),
        confusion_matrix=confusion_matrix(y, predicted, labels=[0, 1]).tolist(),
    )


def evaluate_with_macro_weighted(
    y_true: Any, probabilities: Any, threshold: float = 0.5
) -> dict[str, Any]:
    result = evaluate_predictions(y_true, probabilities, threshold)
    y = np.asarray(y_true).astype(int)
    positive = np.asarray(probabilities)[:, 1]
    predicted = (positive >= threshold).astype(int)
    result_dict = result.to_dict()
    result_dict.update(
        {
            "precision_macro": float(
                precision_score(y, predicted, average="macro", zero_division=0)
            ),
            "precision_weighted": float(
                precision_score(y, predicted, average="weighted", zero_division=0)
            ),
            "recall_macro": float(recall_score(y, predicted, average="macro", zero_division=0)),
            "recall_weighted": float(
                recall_score(y, predicted, average="weighted", zero_division=0)
            ),
        }
    )
    return result_dict


def stratified_cross_validate(
    estimator: Any, X: Any, y: Any, folds: int = 5, random_state: int = 42
) -> pd.DataFrame:
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=random_state)
    scores = cross_validate(
        estimator,
        X,
        y,
        cv=splitter,
        scoring={
            "accuracy": "accuracy",
            "f1": "f1",
            "roc_auc": "roc_auc",
            "pr_auc": "average_precision",
        },
        return_train_score=True,
        n_jobs=None,
        error_score="raise",
    )
    return pd.DataFrame(scores)


def calibrate_probabilities(
    estimator: Any,
    X_train: Any,
    y_train: Any,
    X_validation: Any,
    methods: tuple[str, ...] = ("sigmoid", "isotonic"),
    cv: int = 5,
) -> dict[str, np.ndarray]:
    """Fit calibration maps on training data and predict validation probabilities."""
    calibrated: dict[str, np.ndarray] = {}
    for method in methods:
        calibrator = CalibratedClassifierCV(estimator=estimator, method=method, cv=cv)
        calibrator.fit(X_train, y_train)
        calibrated[method] = calibrator.predict_proba(X_validation)
    return calibrated


def reliability_data(
    y_true: Any, probabilities: Any, n_bins: int = 10
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    positive = np.asarray(probabilities)[:, 1]
    fraction, mean_predicted = calibration_curve(
        np.asarray(y_true), positive, n_bins=n_bins, strategy="uniform"
    )
    counts, edges = np.histogram(positive, bins=n_bins, range=(0.0, 1.0))
    return fraction, mean_predicted, counts


def mcnemar_test(
    y_true: Any, probabilities_a: Any, probabilities_b: Any, threshold: float = 0.5
) -> dict[str, Any]:
    """McNemar exact/binomial test for paired binary predictions."""
    y = np.asarray(y_true).astype(int)
    pred_a = (np.asarray(probabilities_a)[:, 1] >= threshold).astype(int)
    pred_b = (np.asarray(probabilities_b)[:, 1] >= threshold).astype(int)
    correct_a = pred_a == y
    correct_b = pred_b == y
    b = int(np.sum(correct_a & ~correct_b))
    c = int(np.sum(~correct_a & correct_b))
    discordant = b + c
    if discordant == 0:
        statistic = 0.0
        continuity_p_value = 1.0
        exact_p_value = 1.0
    else:
        statistic = (abs(b - c) - 1) ** 2 / discordant
        try:
            from scipy.stats import binomtest, chi2  # type: ignore

            continuity_p_value = float(chi2.sf(statistic, df=1))
            exact_p_value = float(
                binomtest(min(b, c), n=discordant, p=0.5, alternative="two-sided").pvalue
            )
        except ImportError:
            continuity_p_value = float("nan")
            probability = sum(math.comb(discordant, k) for k in range(min(b, c) + 1)) / (2**discordant)
            exact_p_value = float(min(1.0, 2.0 * probability))
    return {
        "b_model_a_only_correct": b,
        "c_model_b_only_correct": c,
        "discordant_pairs": discordant,
        "statistic_continuity_corrected": float(statistic),
        "continuity_corrected_p_value": continuity_p_value,
        "exact_binomial_p_value": exact_p_value,
        "p_value": exact_p_value,
        "interpretation": "Evidence differs at alpha=0.05"
        if exact_p_value < 0.05
        else "No evidence of a difference at alpha=0.05",
    }


def save_metric_result(result: dict[str, Any] | MetricResult, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = result.to_dict() if isinstance(result, MetricResult) else result
    path.write_text(json.dumps(payload, indent=2, default=float), encoding="utf-8")


def benchmark_row(
    model_name: str, y_true: Any, probabilities: Any, threshold: float = 0.5
) -> dict[str, Any]:
    return {"model": model_name, **evaluate_with_macro_weighted(y_true, probabilities, threshold)}


def regression_metrics(y_true: Any, predictions: Any, zero_tolerance: float = 1e-12) -> dict[str, float]:
    """Return RMSE, MAE, MAPE, and R-squared for generic regression fixtures."""
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    actual = np.asarray(y_true, dtype=float).reshape(-1)
    predicted = np.asarray(predictions, dtype=float).reshape(-1)
    if actual.shape != predicted.shape:
        raise ValueError("y_true and predictions must have identical one-dimensional shapes")
    denominator = np.maximum(np.abs(actual), zero_tolerance)
    return {
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "mae": float(mean_absolute_error(actual, predicted)),
        "mape": float(np.mean(np.abs((actual - predicted) / denominator)) * 100.0),
        "r2": float(r2_score(actual, predicted)),
    }


def nested_stratified_cross_validate(
    estimator: Any,
    search_factory: Any,
    X: Any,
    y: Any,
    outer_folds: int = 5,
    inner_folds: int = 3,
    random_state: int = 42,
    scoring: str = "average_precision",
) -> dict[str, Any]:
    """Estimate generalization with outer folds and fit hyperparameters only inside each inner fold."""
    from sklearn.base import clone
    from sklearn.model_selection import StratifiedKFold

    values = np.asarray(y).astype(int)
    outer = StratifiedKFold(n_splits=outer_folds, shuffle=True, random_state=random_state)
    fold_rows: list[dict[str, Any]] = []
    for fold, (train_idx, test_idx) in enumerate(outer.split(X, values)):
        X_inner = X[train_idx] if hasattr(X, "__getitem__") else np.asarray(X)[train_idx]
        X_outer = X[test_idx] if hasattr(X, "__getitem__") else np.asarray(X)[test_idx]
        y_inner, y_outer = values[train_idx], values[test_idx]
        candidate = clone(estimator)
        search = search_factory(candidate, X_inner, y_inner, inner_folds, random_state + fold)
        if not hasattr(search, "best_estimator_") and not isinstance(search, dict):
            search.fit(X_inner, y_inner)
        best = search.get("best_estimator", search) if isinstance(search, dict) else getattr(search, "best_estimator_", search)
        proba = best.predict_proba(X_outer) if hasattr(best, "predict_proba") else best.predict(X_outer)
        if np.asarray(proba).ndim == 1:
            proba = np.column_stack([1.0 - np.asarray(proba), np.asarray(proba)])
        metrics = evaluate_with_macro_weighted(y_outer, proba)
        fold_rows.append(
            {
                "outer_fold": fold,
                "inner_folds": inner_folds,
                "best_params": getattr(search, "best_params_", {}),
                "score": float(metrics.get("pr_auc") or metrics.get("accuracy", 0.0)),
                "metrics": metrics,
            }
        )
    scores = np.asarray([row["score"] for row in fold_rows], dtype=float)
    return {
        "outer_folds": outer_folds,
        "inner_folds": inner_folds,
        "scoring": scoring,
        "random_state": random_state,
        "folds": fold_rows,
        "mean_score": float(scores.mean()),
        "std_score": float(scores.std(ddof=1)) if len(scores) > 1 else 0.0,
        "test_data_used_for_selection": False,
    }


def paired_bootstrap_regression(
    y_true: Any,
    predictions_a: Any,
    predictions_b: Any,
    n_bootstrap: int = 2000,
    random_state: int = 42,
    metric: str = "rmse",
    confidence_level: float = 0.95,
) -> dict[str, float | int | str]:
    """Estimate a paired bootstrap CI for the difference in two regression metrics."""
    actual = np.asarray(y_true, dtype=float).reshape(-1)
    first = np.asarray(predictions_a, dtype=float).reshape(-1)
    second = np.asarray(predictions_b, dtype=float).reshape(-1)
    if actual.shape != first.shape or actual.shape != second.shape:
        raise ValueError("Paired bootstrap inputs must have identical shapes")
    if n_bootstrap < 10 or not 0.0 < confidence_level < 1.0:
        raise ValueError("n_bootstrap must be at least 10 and confidence_level must lie in (0, 1)")
    if metric not in {"rmse", "mae", "mape", "r2"}:
        raise ValueError("metric must be rmse, mae, mape, or r2")
    rng = np.random.default_rng(random_state)

    def score(target: np.ndarray, pred: np.ndarray) -> float:
        return regression_metrics(target, pred)[metric]

    observed = score(actual, first) - score(actual, second)
    differences = np.empty(n_bootstrap, dtype=float)
    for index in range(n_bootstrap):
        sample = rng.integers(0, len(actual), size=len(actual))
        differences[index] = score(actual[sample], first[sample]) - score(actual[sample], second[sample])
    alpha = (1.0 - confidence_level) / 2.0
    low, high = np.quantile(differences, [alpha, 1.0 - alpha])
    return {
        "metric": metric,
        "observed_difference_a_minus_b": float(observed),
        "ci_low": float(low),
        "ci_high": float(high),
        "confidence_level": float(confidence_level),
        "n_bootstrap": int(n_bootstrap),
        "random_state": int(random_state),
    }
