"""Explicit model factories for topics named in the 25SC2107E handout.

The project is a binary fake-news classifier, so regression is represented by a
small generic LinearRegression factory for CO2/M2 mathematical/engineering
coverage rather than pretending that regression is the project's target task.
AdaBoost and One-Class SVM cover the handout's M3/M4 methods that were not
previously exposed as first-class factories.

All estimators must be fitted inside the caller's training/CV pipeline.
"""

from __future__ import annotations

from typing import Any

from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM


def build_linear_regression(*, fit_intercept: bool = True, positive: bool = False) -> LinearRegression:
    """Return the ordinary least-squares model named by CO2/M2."""
    return LinearRegression(fit_intercept=fit_intercept, positive=positive)


def build_multinomial_logistic(
    *, C: float = 1.0, max_iter: int = 2000, random_state: int = 42
) -> Pipeline:
    """Return an explicit softmax/multinomial logistic classifier.

    The factory is useful for multi-class experiments and handout demonstrations;
    the production fake/real task remains binary.
    """
    if C <= 0:
        raise ValueError("C must be positive")
    estimator = LogisticRegression(
        C=C,
        max_iter=max_iter,
        solver="lbfgs",
        multi_class="multinomial",
        random_state=random_state,
    )
    return Pipeline(
        [
            ("scaler", StandardScaler(with_mean=False)),
            ("classifier", estimator),
        ]
    )


def build_adaboost(
    *, n_estimators: int = 200, learning_rate: float = 0.5, random_state: int = 42
) -> AdaBoostClassifier:
    """Return AdaBoost for the M3 boosting comparison."""
    if n_estimators < 1 or learning_rate <= 0:
        raise ValueError("n_estimators must be >= 1 and learning_rate must be positive")
    return AdaBoostClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        random_state=random_state,
    )


def build_one_class_svm(
    *, nu: float = 0.05, kernel: str = "rbf", gamma: str | float = "scale"
) -> OneClassSVM:
    """Return One-Class SVM for M4 anomaly-detection demonstrations."""
    if not 0.0 < nu <= 1.0:
        raise ValueError("nu must be in (0, 1]")
    return OneClassSVM(nu=nu, kernel=kernel, gamma=gamma)


def anomaly_labels(model: OneClassSVM, X: Any) -> Any:
    """Map One-Class SVM's +1/-1 output to 0=normal, 1=anomaly."""
    labels = model.predict(X)
    return (labels == -1).astype(int)
