"""Classical supervised baselines for CO2/M2 and CO3/M3.

The pipelines intentionally separate the TF-IDF fit from model fitting so callers
can enforce the train-only fitting rule. References SRC-004 through SRC-006 and
SRC-021 through SRC-023 in docs/sources.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


def build_logistic_model(
    penalty: str = "l2", C: float = 1.0, max_iter: int = 2000, random_state: int = 42
) -> Pipeline:
    """Build L1/L2/ElasticNet Logistic Regression.

    Compliant with M2: Linear Models. Scaling uses ``with_mean=False`` to preserve
    sparse TF-IDF matrices while maintaining numerical feature-scale compatibility.
    """
    if penalty not in {"l1", "l2", "elasticnet"}:
        raise ValueError("penalty must be l1, l2, or elasticnet")
    solver = "saga" if penalty in {"l1", "elasticnet"} else "liblinear"
    classifier_kwargs = {
        "penalty": penalty,
        "C": C,
        "solver": solver,
        "max_iter": max_iter,
        "random_state": random_state,
        "class_weight": "balanced",
    }
    if penalty == "elasticnet":
        classifier_kwargs["l1_ratio"] = 0.5
    classifier = LogisticRegression(**classifier_kwargs)
    return Pipeline([("scaler", StandardScaler(with_mean=False)), ("classifier", classifier)])


def build_decision_tree(
    max_depth: int | None = None, ccp_alpha: float = 0.0, random_state: int = 42
) -> DecisionTreeClassifier:
    """Build a prunable Decision Tree compliant with M3/CO3."""
    return DecisionTreeClassifier(
        criterion="gini",
        max_depth=max_depth,
        ccp_alpha=ccp_alpha,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
    )


def build_random_forest(
    n_estimators: int = 300, max_depth: int | None = None, random_state: int = 42
) -> RandomForestClassifier:
    """Build a bagged forest with OOB error enabled."""
    return RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        class_weight="balanced",
        oob_score=True,
        bootstrap=True,
        n_jobs=-1,
        random_state=random_state,
    )


def build_xgboost(random_state: int = 42) -> Any:
    """Build XGBoost lazily so classical linear paths do not require it at import time."""
    try:
        from xgboost import XGBClassifier  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install the xgboost optional dependency to use XGBoost") from exc
    return XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        tree_method="hist",
        random_state=random_state,
        n_jobs=-1,
    )


def build_lightgbm(random_state: int = 42) -> Any:
    """Build LightGBM lazily and expose a compatible classifier interface."""
    try:
        from lightgbm import LGBMClassifier  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install the lightgbm optional dependency to use LightGBM") from exc
    return LGBMClassifier(
        n_estimators=300,
        num_leaves=31,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.8,
        objective="binary",
        random_state=random_state,
        n_jobs=-1,
        verbosity=-1,
    )


def train_estimator(estimator: Any, X_train: Any, y_train: Any) -> Any:
    estimator.fit(X_train, y_train)
    return estimator


def coefficient_table(model: Pipeline, feature_names: np.ndarray) -> pd.DataFrame:
    classifier = model.named_steps["classifier"]
    coefficients = np.asarray(classifier.coef_).reshape(-1)
    frame = pd.DataFrame({"feature": feature_names, "coefficient": coefficients})
    frame["absolute_coefficient"] = frame["coefficient"].abs()
    return frame.sort_values("absolute_coefficient", ascending=False).reset_index(drop=True)


def gini_importance_table(model: Any, feature_names: np.ndarray) -> pd.DataFrame:
    if not hasattr(model, "feature_importances_"):
        raise TypeError("Estimator does not expose feature_importances_")
    values = np.asarray(model.feature_importances_)
    return (
        pd.DataFrame({"feature": feature_names, "importance": values})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def permutation_importance_table(
    model: Any,
    X: Any,
    y: Any,
    feature_names: np.ndarray,
    random_state: int = 42,
    n_repeats: int = 5,
) -> pd.DataFrame:
    result = permutation_importance(
        model,
        X,
        y,
        n_repeats=n_repeats,
        random_state=random_state,
        scoring="average_precision",
        n_jobs=-1,
    )
    return (
        pd.DataFrame(
            {
                "feature": feature_names,
                "importance_mean": result.importances_mean,
                "importance_std": result.importances_std,
            }
        )
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )


def shap_values(
    model: Any, X: Any, feature_names: np.ndarray, max_samples: int = 1000
) -> pd.DataFrame:
    """Return a compact TreeExplainer summary; SHAP remains optional at runtime."""
    try:
        import shap  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install shap to generate TreeExplainer outputs") from exc
    sample = X[:max_samples]
    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(sample)
    if isinstance(values, list):
        values = values[-1]
    mean_abs = np.asarray(np.abs(values).mean(axis=0)).reshape(-1)
    return (
        pd.DataFrame({"feature": feature_names, "mean_abs_shap": mean_abs})
        .sort_values("mean_abs_shap", ascending=False)
        .reset_index(drop=True)
    )


def save_importance_table(frame: pd.DataFrame, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
