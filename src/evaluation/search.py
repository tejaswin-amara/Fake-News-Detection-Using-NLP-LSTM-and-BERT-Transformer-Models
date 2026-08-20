"""Leakage-safe hyperparameter search utilities for M5/CO5.

Search operates on the training split or inner cross-validation split only. The
final test set must never be passed to these functions. References SRC-024 and
SRC-025.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, StratifiedKFold


@dataclass
class SearchResult:
    search_type: str
    best_params: dict[str, Any]
    best_score: float
    cv_folds: int
    scoring: str
    random_state: int
    test_data_used: bool = False
    trials: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _cv(folds: int, random_state: int) -> StratifiedKFold:
    if folds < 2:
        raise ValueError("cv_folds must be at least 2")
    return StratifiedKFold(n_splits=folds, shuffle=True, random_state=random_state)


def grid_search(
    estimator: Any,
    parameter_grid: dict[str, list[Any]],
    X: Any,
    y: Any,
    cv_folds: int = 5,
    scoring: str = "average_precision",
    random_state: int = 42,
) -> GridSearchCV:
    search = GridSearchCV(
        estimator, parameter_grid, scoring=scoring, cv=_cv(cv_folds, random_state),
        n_jobs=None, refit=True, return_train_score=True,
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
    search = RandomizedSearchCV(
        estimator, parameter_distributions, n_iter=n_iter, scoring=scoring,
        cv=_cv(cv_folds, random_state), random_state=random_state, n_jobs=None,
        refit=True, return_train_score=True,
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
    cv_folds: int = 5,
) -> dict[str, Any]:
    """Optional Optuna/TPE Bayesian search with bounded deterministic trials."""
    try:
        import optuna  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install optuna to use the Bayesian search path") from exc
    from sklearn.base import clone
    from sklearn.model_selection import cross_val_score

    cv = _cv(cv_folds, random_state)

    def objective(trial: Any) -> float:
        params: dict[str, Any] = {}
        for name, spec in search_space.items():
            if spec["type"] == "float":
                params[name] = trial.suggest_float(name, spec["low"], spec["high"], log=spec.get("log", False))
            elif spec["type"] == "int":
                params[name] = trial.suggest_int(name, spec["low"], spec["high"])
            elif spec["type"] == "categorical":
                params[name] = trial.suggest_categorical(name, spec["choices"])
            else:
                raise ValueError(f"Unknown Bayesian search specification: {spec['type']}")
        candidate = clone(estimator).set_params(**params)
        return float(cross_val_score(candidate, X, y, cv=cv, scoring=scoring).mean())

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=random_state))
    study.optimize(objective, n_trials=n_trials)
    best = clone(estimator).set_params(**study.best_params).fit(X, y)
    return {
        "study": study,
        "best_estimator": best,
        "best_params": study.best_params,
        "best_value": float(study.best_value),
        "search_result": SearchResult(
            search_type="bayesian", best_params=study.best_params,
            best_score=float(study.best_value), cv_folds=cv_folds,
            scoring=scoring, random_state=random_state,
            trials=[{"number": trial.number, "value": trial.value, "state": str(trial.state)} for trial in study.trials],
        ),
    }


def search_result(search: Any, search_type: str, cv_folds: int, scoring: str, random_state: int) -> SearchResult:
    """Normalize GridSearchCV/RandomizedSearchCV/Optuna outputs."""
    if isinstance(search, dict):
        return search.get("search_result") or SearchResult(
            search_type=search_type, best_params=search["best_params"], best_score=float(search["best_value"]),
            cv_folds=cv_folds, scoring=scoring, random_state=random_state,
        )
    trials = None
    if hasattr(search, "cv_results_"):
        trials = [
            {"params": params, "mean_test_score": float(score), "mean_train_score": float(train)}
            for params, score, train in zip(
                search.cv_results_["params"], search.cv_results_["mean_test_score"], search.cv_results_["mean_train_score"], strict=False
            )
        ]
    return SearchResult(
        search_type=search_type, best_params=dict(search.best_params_), best_score=float(search.best_score_),
        cv_folds=cv_folds, scoring=scoring, random_state=random_state, trials=trials,
    )


def save_search_result(result: SearchResult | dict[str, Any], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = result.to_dict() if isinstance(result, SearchResult) else result
    payload = json.loads(json.dumps(payload, default=str))
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output
