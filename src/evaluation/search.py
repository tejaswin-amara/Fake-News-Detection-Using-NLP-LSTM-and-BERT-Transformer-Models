"""Hyperparameter search utilities for M5/CO5.

References SRC-024 and SRC-025 in docs/sources.md. Search operates on the
training split or an inner cross-validation split; the final test set must not
be passed to these functions during model selection.
"""

from __future__ import annotations

from typing import Any

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, StratifiedKFold


def grid_search(
    estimator: Any,
    parameter_grid: dict[str, list[Any]],
    X: Any,
    y: Any,
    cv_folds: int = 5,
    scoring: str = "average_precision",
    random_state: int = 42,
) -> GridSearchCV:
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    search = GridSearchCV(
        estimator,
        parameter_grid,
        scoring=scoring,
        cv=cv,
        n_jobs=None,
        refit=True,
        return_train_score=True,
    )
    search.fit(X, y)
    return search


def random_search(
    estimator: Any,
    parameter_distributions: dict[str, Any],
    X: Any,
    y: Any,
    n_iter: int = 20,
    cv_folds: int = 5,
    scoring: str = "average_precision",
    random_state: int = 42,
) -> RandomizedSearchCV:
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    search = RandomizedSearchCV(
        estimator,
        parameter_distributions,
        n_iter=n_iter,
        scoring=scoring,
        cv=cv,
        random_state=random_state,
        n_jobs=None,
        refit=True,
        return_train_score=True,
    )
    search.fit(X, y)
    return search


def bayesian_search(
    estimator: Any,
    search_space: dict[str, Any],
    X: Any,
    y: Any,
    n_trials: int = 25,
    scoring: str = "average_precision",
    random_state: int = 42,
) -> Any:
    """Optional Optuna-backed Bayesian search; unavailable means a clear error."""
    try:
        import optuna  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install optuna to use the Bayesian search path") from exc
    from sklearn.base import clone
    from sklearn.model_selection import cross_val_score

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)

    def objective(trial):
        params = {}
        for name, spec in search_space.items():
            if spec["type"] == "float":
                params[name] = trial.suggest_float(
                    name, spec["low"], spec["high"], log=spec.get("log", False)
                )
            elif spec["type"] == "int":
                params[name] = trial.suggest_int(name, spec["low"], spec["high"])
            elif spec["type"] == "categorical":
                params[name] = trial.suggest_categorical(name, spec["choices"])
            else:
                raise ValueError(f"Unknown Bayesian search specification: {spec['type']}")
        candidate = clone(estimator).set_params(**params)
        return float(cross_val_score(candidate, X, y, cv=cv, scoring=scoring).mean())

    study = optuna.create_study(
        direction="maximize", sampler=optuna.samplers.TPESampler(seed=random_state)
    )
    study.optimize(objective, n_trials=n_trials)
    best = clone(estimator).set_params(**study.best_params).fit(X, y)
    return {
        "study": study,
        "best_estimator": best,
        "best_params": study.best_params,
        "best_value": study.best_value,
    }
