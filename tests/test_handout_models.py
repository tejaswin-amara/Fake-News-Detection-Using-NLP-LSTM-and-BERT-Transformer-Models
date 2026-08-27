import numpy as np
import pytest

from src.models.handout_models import (
    anomaly_labels,
    build_adaboost,
    build_linear_regression,
    build_multinomial_logistic,
    build_one_class_svm,
)


def test_linear_regression_factory_is_explicit() -> None:
    model = build_linear_regression()
    X = np.array([[0.0], [1.0], [2.0], [3.0]])
    y = np.array([0.0, 2.0, 4.0, 6.0])
    model.fit(X, y)
    assert np.allclose(model.predict([[4.0]]), [8.0])


def test_multinomial_logistic_supports_three_classes() -> None:
    X = np.array([
        [0.0, 0.0], [0.1, 0.0],
        [2.0, 2.0], [2.1, 2.0],
        [4.0, 0.0], [4.1, 0.1],
    ])
    y = np.array([0, 0, 1, 1, 2, 2])
    model = build_multinomial_logistic()
    model.fit(X, y)
    probabilities = model.predict_proba(X)
    assert probabilities.shape == (6, 3)
    assert np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-7)


def test_adaboost_factory_trains() -> None:
    X = np.array([[0.0], [0.2], [1.0], [1.2], [2.0], [2.2]])
    y = np.array([0, 0, 0, 1, 1, 1])
    model = build_adaboost(n_estimators=10)
    model.fit(X, y)
    assert model.predict_proba(X).shape == (6, 2)


def test_one_class_svm_maps_anomalies() -> None:
    X = np.array([[0.0], [0.1], [0.2], [0.3], [10.0]])
    model = build_one_class_svm(nu=0.2)
    model.fit(X[:4])
    labels = anomaly_labels(model, X)
    assert labels.shape == (5,)
    assert set(labels).issubset({0, 1})


def test_invalid_factories_fail_fast() -> None:
    with pytest.raises(ValueError):
        build_adaboost(n_estimators=0)
    with pytest.raises(ValueError):
        build_one_class_svm(nu=0)
    with pytest.raises(ValueError):
        build_multinomial_logistic(C=0)
