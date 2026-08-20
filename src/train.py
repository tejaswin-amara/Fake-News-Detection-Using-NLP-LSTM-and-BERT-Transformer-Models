"""Training orchestration for classical models with optional search and MLflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.config import load_config
from src.evaluation.search import (
    bayesian_search,
    grid_search,
    random_search,
    save_search_result,
    search_result,
)
from src.features.text import TfidfTextPipeline
from src.models.classical import (
    build_decision_tree,
    build_lightgbm,
    build_logistic_model,
    build_random_forest,
    build_xgboost,
)
from src.serving.export import artifact_metadata
from src.serving.predictor import PackagedTextModel
from src.tracking import experiment_run, log_artifact, log_metrics, log_parameters


def select_model(name: str, seed: int):
    if name == "logistic_l1":
        return build_logistic_model("l1", random_state=seed)
    if name == "logistic_l2":
        return build_logistic_model("l2", random_state=seed)
    if name == "logistic_elasticnet":
        return build_logistic_model("elasticnet", random_state=seed)
    if name == "logistic_multinomial":
        return build_logistic_model("l2", random_state=seed, multi_class="multinomial")
    if name == "decision_tree":
        return build_decision_tree(ccp_alpha=0.001, random_state=seed)
    if name == "random_forest":
        return build_random_forest(random_state=seed)
    if name == "xgboost":
        return build_xgboost(random_state=seed)
    if name == "lightgbm":
        return build_lightgbm(random_state=seed)
    raise ValueError(f"Unknown model: {name}")


def default_parameter_space(name: str) -> dict[str, list[Any]]:
    if name.startswith("logistic"):
        return {"classifier__C": [0.25, 1.0, 4.0]}
    if name == "decision_tree":
        return {"max_depth": [None, 4, 8], "ccp_alpha": [0.0, 0.001]}
    if name == "random_forest":
        return {"n_estimators": [100, 200], "max_depth": [None, 10]}
    if name == "xgboost":
        return {"max_depth": [4, 6], "learning_rate": [0.05, 0.1]}
    if name == "lightgbm":
        return {"num_leaves": [15, 31], "max_depth": [-1, 8]}
    raise ValueError(f"No default search space for {name}")


def run_search(model: Any, search_type: str, X: Any, y: Any, args: argparse.Namespace) -> tuple[Any, dict[str, Any] | None]:
    if search_type == "none":
        model.fit(X, y)
        return model, None
    space = default_parameter_space(args.model)
    if search_type == "grid":
        fitted = grid_search(model, space, X, y, cv_folds=args.cv_folds, scoring=args.scoring, random_state=args.seed)
        result = search_result(fitted, "grid", args.cv_folds, args.scoring, args.seed)
        return fitted.best_estimator_, result.to_dict()
    if search_type == "random":
        fitted = random_search(model, space, X, y, n_iter=args.n_iter, cv_folds=args.cv_folds, scoring=args.scoring, random_state=args.seed)
        result = search_result(fitted, "random", args.cv_folds, args.scoring, args.seed)
        return fitted.best_estimator_, result.to_dict()
    if search_type == "bayesian":
        bayesian_space = {
            key: {"type": "float", "low": min(values), "high": max(values), "log": True}
            for key, values in space.items()
            if all(isinstance(value, (int, float)) for value in values)
        }
        result = bayesian_search(model, bayesian_space, X, y, n_trials=args.n_iter, scoring=args.scoring, random_state=args.seed, cv_folds=args.cv_folds)
        return result["best_estimator"], result["search_result"].to_dict()
    raise ValueError("search_type must be none, grid, random, or bayesian")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a fake-news model with optional hyperparameter search")
    parser.add_argument("--train", default="data/processed/train.csv")
    parser.add_argument("--output", default="artifacts/models/logistic_l2.joblib")
    parser.add_argument("--model", default="logistic_l2")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--search-type", choices=["none", "grid", "random", "bayesian"], default="none")
    parser.add_argument("--search-output", default="reports/evaluation/search.json")
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--n-iter", type=int, default=20)
    parser.add_argument("--scoring", default="average_precision")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--mlflow", action="store_true", help="Enable MLflow logging for this run")
    parser.add_argument("--tracking-uri", default=None)
    parser.add_argument("--experiment-name", default=None)
    parser.add_argument("--artifact-location", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    seed = config.seed if args.seed is None else args.seed
    frame = pd.read_csv(args.train)
    if "content" not in frame or "label" not in frame:
        raise ValueError("Training CSV must contain content and label columns")
    tfidf_config = config.values["text"]["tfidf"]
    tfidf = TfidfTextPipeline(
        ngram_range=tuple(tfidf_config["ngram_range"]), min_df=tfidf_config["min_df"],
        max_df=tfidf_config["max_df"], max_features=tfidf_config["max_features"],
        sublinear_tf=tfidf_config["sublinear_tf"],
    )
    X_train = tfidf.fit_transform(frame["content"].fillna(""))
    y_train = frame["label"].astype(int).to_numpy()
    model = select_model(args.model, seed)
    search_type = args.search_type
    tracking = config.values.get("tracking", {})
    tracking_enabled = bool(args.mlflow or tracking.get("enabled", False))
    tracking_uri = args.tracking_uri or str(tracking.get("uri", "mlruns"))
    experiment_name = args.experiment_name or str(tracking.get("experiment_name", "fake-news-detection"))
    artifact_location = args.artifact_location or tracking.get("artifact_location")

    with experiment_run(enabled=tracking_enabled, tracking_uri=tracking_uri, experiment_name=experiment_name, artifact_location=artifact_location, run_name=args.model) as run:
        fitted_model, search_payload = run_search(model, search_type, X_train, y_train, args)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        artifact = {
            "model": PackagedTextModel(tfidf, fitted_model),
            "metadata": artifact_metadata(
                args.model,
                {"representation": "tfidf", "feature_count": int(X_train.shape[1]), "label_mapping": {"real": 0, "fake": 1}, "search_type": search_type, "search": search_payload},
                seed,
            ),
        }
        joblib.dump(artifact, output)
        if search_payload is not None:
            save_search_result(search_payload, args.search_output)
        log_parameters(run, {"model": args.model, "train_rows": len(frame), "feature_count": X_train.shape[1], "random_seed": seed, "config": args.config, "search_type": search_type, "cv_folds": args.cv_folds})
        if search_payload is not None:
            log_metrics(run, {"best_cv_score": float(search_payload["best_score"])})
            log_artifact(run, args.search_output)
        if tracking.get("log_config", True):
            log_artifact(run, args.config)
        log_artifact(run, output)

    print(json.dumps({"model": args.model, "output": str(output), "rows": len(frame), "features": X_train.shape[1], "search_type": search_type, "mlflow_enabled": tracking_enabled, "search_report": args.search_output if search_payload else None}, indent=2))


if __name__ == "__main__":
    main()
