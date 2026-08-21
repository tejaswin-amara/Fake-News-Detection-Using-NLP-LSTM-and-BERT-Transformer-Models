"""Classical supervised models and explainability utilities for CO2/M2 and CO3/M3.

References SRC-004 through SRC-006 and SRC-021 through SRC-023. Learned text and
feature transforms must be fit inside the caller's training/CV pipeline only.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNet, Lasso, LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


def _sparse_scaler() -> StandardScaler:
    return StandardScaler(with_mean=False)


def build_ridge_model(alpha: float = 1.0, random_state: int = 42) -> Pipeline:
    return Pipeline([("scaler", _sparse_scaler()), ("regressor", Ridge(alpha=alpha))])


def build_lasso_model(alpha: float = 0.001, random_state: int = 42) -> Pipeline:
    return Pipeline([("scaler", _sparse_scaler()), ("regressor", Lasso(alpha=alpha, max_iter=5000))])


def build_elasticnet_model(
    alpha: float = 0.001, l1_ratio: float = 0.5, random_state: int = 42
) -> Pipeline:
    return Pipeline(
        [("scaler", _sparse_scaler()), ("regressor", ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=5000, random_state=random_state))]
    )


def build_logistic_model(
    penalty: str = "l2",
    C: float = 1.0,
    max_iter: int = 2000,
    random_state: int = 42,
    multi_class: str = "auto",
) -> Pipeline:
    """Build binary or multinomial Logistic Regression for sparse TF-IDF."""
    if penalty not in {"l1", "l2", "elasticnet"}:
        raise ValueError("penalty must be l1, l2, or elasticnet")
    solver = "saga" if penalty in {"l1", "elasticnet"} or multi_class == "multinomial" else "liblinear"
    classifier_kwargs: dict[str, Any] = {
        "penalty": penalty,
        "C": C,
        "solver": solver,
        "max_iter": max_iter,
        "random_state": random_state,
        "class_weight": "balanced",
    }
    if "multi_class" in inspect.signature(LogisticRegression).parameters:
        classifier_kwargs["multi_class"] = multi_class
    if penalty == "elasticnet":
        classifier_kwargs["l1_ratio"] = 0.5
    classifier = LogisticRegression(**classifier_kwargs)
    return Pipeline([("scaler", _sparse_scaler()), ("classifier", classifier)])


def build_decision_tree(
    max_depth: int | None = None,
    ccp_alpha: float = 0.0,
    criterion: str = "gini",
    random_state: int = 42,
) -> DecisionTreeClassifier:
    if criterion not in {"gini", "entropy", "log_loss"}:
        raise ValueError("criterion must be gini, entropy, or log_loss")
    return DecisionTreeClassifier(
        criterion=criterion,
        max_depth=max_depth,
        ccp_alpha=ccp_alpha,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
    )


def build_random_forest(
    n_estimators: int = 300, max_depth: int | None = None, random_state: int = 42
) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        class_weight="balanced",
        oob_score=True,
        bootstrap=True,
        n_jobs=-1,
        random_state=random_state,
    )


def compute_scale_pos_weight(y: Any) -> float:
    """Compute negative-to-positive ratio from the training labels only."""
    labels = np.asarray(y, dtype=int).reshape(-1)
    positives = int(np.sum(labels == 1))
    negatives = int(np.sum(labels == 0))
    if positives < 1 or negatives < 1:
        raise ValueError("Both classes are required to compute scale_pos_weight")
    return float(negatives / positives)


def build_xgboost(random_state: int = 42, scale_pos_weight: float = 1.0, **overrides: Any) -> Any:
    try:
        from xgboost import XGBClassifier  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install the xgboost optional dependency to use XGBoost") from exc
    params = {
        "n_estimators": 300,
        "max_depth": 6,
        "learning_rate": 0.08,
        "subsample": 0.9,
        "colsample_bytree": 0.8,
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "tree_method": "hist",
        "random_state": random_state,
        "n_jobs": -1,
        "scale_pos_weight": float(scale_pos_weight),
    }
    params.update(overrides)
    return XGBClassifier(**params)


def build_lightgbm(random_state: int = 42, is_unbalance: bool = True, **overrides: Any) -> Any:
    try:
        from lightgbm import LGBMClassifier  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install the lightgbm optional dependency to use LightGBM") from exc
    params = {
        "n_estimators": 300,
        "num_leaves": 31,
        "max_depth": -1,
        "learning_rate": 0.05,
        "subsample": 0.9,
        "colsample_bytree": 0.8,
        "boosting_type": "gbdt",
        "objective": "binary",
        "random_state": random_state,
        "n_jobs": -1,
        "verbosity": -1,
        "is_unbalance": bool(is_unbalance),
    }
    params.update(overrides)
    return LGBMClassifier(**params)


def train_estimator(estimator: Any, X_train: Any, y_train: Any) -> Any:
    estimator.fit(X_train, y_train)
    return estimator


def model_metadata(model: Any) -> dict[str, Any]:
    return {
        "estimator_class": model.__class__.__name__,
        "has_predict_proba": bool(hasattr(model, "predict_proba")),
        "has_feature_importances": bool(hasattr(model, "feature_importances_")),
        "parameters": model.get_params(deep=True) if hasattr(model, "get_params") else {},
    }


def _validate_feature_names(feature_names: np.ndarray, width: int) -> np.ndarray:
    names = np.asarray(feature_names, dtype=object)
    if len(names) != width:
        raise ValueError(f"Feature-name count {len(names)} does not match model width {width}")
    return names


def coefficient_table(model: Pipeline, feature_names: np.ndarray) -> pd.DataFrame:
    classifier = model.named_steps.get("classifier", model.named_steps.get("regressor"))
    coefficients = np.asarray(classifier.coef_ if hasattr(classifier, "coef_") else classifier.coef_)
    if coefficients.ndim > 1:
        coefficients = coefficients.mean(axis=0)
    coefficients = coefficients.reshape(-1)
    names = _validate_feature_names(feature_names, len(coefficients))
    frame = pd.DataFrame({"feature": names, "coefficient": coefficients})
    frame["absolute_coefficient"] = frame["coefficient"].abs()
    return frame.sort_values("absolute_coefficient", ascending=False).reset_index(drop=True)


def gini_importance_table(model: Any, feature_names: np.ndarray) -> pd.DataFrame:
    if not hasattr(model, "feature_importances_"):
        raise TypeError("Estimator does not expose feature_importances_")
    values = np.asarray(model.feature_importances_).reshape(-1)
    names = _validate_feature_names(feature_names, len(values))
    return pd.DataFrame({"feature": names, "importance": values}).sort_values(
        "importance", ascending=False
    ).reset_index(drop=True)


def permutation_importance_table(
    model: Any,
    X: Any,
    y: Any,
    feature_names: np.ndarray,
    random_state: int = 42,
    n_repeats: int = 5,
) -> pd.DataFrame:
    values = X.toarray() if hasattr(X, "toarray") else np.asarray(X)
    result = permutation_importance(
        model, values, y, n_repeats=n_repeats, random_state=random_state,
        scoring="average_precision", n_jobs=-1,
    )
    names = _validate_feature_names(feature_names, len(result.importances_mean))
    return pd.DataFrame(
        {"feature": names, "importance_mean": result.importances_mean, "importance_std": result.importances_std}
    ).sort_values("importance_mean", ascending=False).reset_index(drop=True)


def shap_values(
    model: Any, X: Any, feature_names: np.ndarray, max_samples: int = 1000
) -> pd.DataFrame:
    """Return a compact TreeExplainer summary; SHAP remains optional at runtime."""
    try:
        import shap  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install shap to generate TreeExplainer outputs") from exc
    sample = X[:max_samples].toarray() if hasattr(X[:max_samples], "toarray") else np.asarray(X[:max_samples])
    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(sample)
    if isinstance(values, list):
        values = values[-1]
    if hasattr(values, "values"):
        values = values.values
    values_array = np.asarray(values)
    if values_array.ndim == 3:
        values_array = values_array[:, :, -1]
    mean_abs = np.abs(values_array).mean(axis=0).reshape(-1)
    names = _validate_feature_names(feature_names, len(mean_abs))
    return pd.DataFrame({"feature": names, "mean_abs_shap": mean_abs}).sort_values(
        "mean_abs_shap", ascending=False
    ).reset_index(drop=True)


def save_importance_table(frame: pd.DataFrame, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
