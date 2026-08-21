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
    compute_scale_pos_weight,
)
from src.serving.export import artifact_metadata
from src.serving.predictor import PackagedTextModel
from src.tracking import experiment_run, log_artifact, log_metrics, log_parameters


def select_model(name: str, seed: int, y_train: Any | None = None):
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
        weight = compute_scale_pos_weight(y_train) if y_train is not None else 1.0
        return build_xgboost(random_state=seed, scale_pos_weight=weight)
    if name == "lightgbm":
        return build_lightgbm(random_state=seed, is_unbalance=True)
    raise ValueError(f"Unknown model: {name}")


def default_parameter_space(name: str, model_config: dict[str, Any] | None = None) -> dict[str, list[Any]]:
    config_key = "logistic" if name.startswith("logistic") else name
    configured = (model_config or {}).get(config_key)
    if isinstance(configured, dict):
        mapped: dict[str, list[Any]] = {}
        for key, values in configured.items():
            if isinstance(values, list):
                if key == "C_values":
                    mapped["classifier__C"] = values
                elif key not in {"penalties", "multi_class", "l1_ratio"}:
                    mapped[key] = values
        if mapped:
            return mapped
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
    space = default_parameter_space(args.model, getattr(args, "model_config", None))
    if search_type == "grid":
        fitted = grid_search(model, space, X, y, cv_folds=args.cv_folds, scoring=args.scoring, random_state=args.seed, n_jobs=args.n_jobs)
        result = search_result(fitted, "grid", args.cv_folds, args.scoring, args.seed)
        return fitted.best_estimator_, result.to_dict()
    if search_type == "random":
        fitted = random_search(model, space, X, y, n_iter=args.n_iter, cv_folds=args.cv_folds, scoring=args.scoring, random_state=args.seed, n_jobs=args.n_jobs)
        result = search_result(fitted, "random", args.cv_folds, args.scoring, args.seed)
        return fitted.best_estimator_, result.to_dict()
    if search_type == "bayesian":
        bayesian_space = {
            key: {"type": "float", "low": min(values), "high": max(values), "log": True}
            for key, values in space.items()
            if all(isinstance(value, (int, float)) for value in values)
        }
        result = bayesian_search(model, bayesian_space, X, y, n_trials=args.n_iter, scoring=args.scoring, random_state=args.seed, cv_folds=args.cv_folds, n_jobs=args.n_jobs)
        return result["best_estimator"], result["search_result"].to_dict()
    raise ValueError("search_type must be none, grid, random, or bayesian")


def _train_lstm_path(frame: pd.DataFrame, validation: pd.DataFrame, args: argparse.Namespace, seed: int, models_config: dict[str, Any]) -> None:
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    from tensorflow.keras.preprocessing.text import Tokenizer

    from src.models.lstm import LSTMConfig, build_bilstm_model, train_bilstm

    lstm_config = models_config.get("lstm", {})
    max_length = int(args.max_length or 400)
    tokenizer = Tokenizer(num_words=int(lstm_config.get("vocab_size", 30_000)), oov_token="<OOV>")
    tokenizer.fit_on_texts(frame["content"].fillna("").astype(str).tolist())
    X_train = pad_sequences(tokenizer.texts_to_sequences(frame["content"].fillna("")), maxlen=max_length)
    X_validation = pad_sequences(tokenizer.texts_to_sequences(validation["content"].fillna("")), maxlen=max_length)
    config = LSTMConfig(vocab_size=min(int(lstm_config.get("vocab_size", 30_000)), len(tokenizer.word_index) + 1), max_length=max_length, embedding_dim=int(lstm_config.get("embedding_dimensions", [100])[0]))
    model = build_bilstm_model(config)
    output = Path(args.output)
    train_bilstm(model, X_train, frame["label"].astype(int).to_numpy(), X_validation, validation["label"].astype(int).to_numpy(), output.parent / f"{output.stem}_lstm", epochs=args.epochs or int(lstm_config.get("smoke_epochs", 1)), batch_size=args.batch_size or int(lstm_config.get("smoke_batch_size", 4)))
    output.parent.mkdir(parents=True, exist_ok=True)
    model.save(output.with_suffix(".keras"))
    joblib.dump({"tokenizer": tokenizer, "metadata": {"model_name": "bilstm", "max_length": max_length, "random_seed": seed}}, output.with_suffix(".tokenizer.joblib"))


def _train_bert_path(frame: pd.DataFrame, validation: pd.DataFrame, args: argparse.Namespace, models_config: dict[str, Any]) -> None:
    from src.models.bert import BertConfig, load_components, tokenize_dataset, train_bert

    bert_config = models_config.get("bert", {})
    model_config = BertConfig(model_name=str(bert_config.get("model_name", "bert-base-uncased")), epochs=args.epochs or int(bert_config.get("smoke_epochs", 1)), batch_size=args.batch_size or int(bert_config.get("smoke_batch_size", 4)), learning_rate=float(bert_config.get("learning_rates", [2e-5])[0]))
    tokenizer, _ = load_components(model_config)
    train_dataset = tokenize_dataset(frame["content"].fillna("").astype(str).tolist(), frame["label"].astype(int).tolist(), tokenizer, model_config.max_length)
    validation_dataset = tokenize_dataset(validation["content"].fillna("").astype(str).tolist(), validation["label"].astype(int).tolist(), tokenizer, model_config.max_length)
    train_bert(train_dataset, validation_dataset, model_config, args.output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a fake-news model with optional hyperparameter search")
    parser.add_argument("--validation", default="data/processed/validation.csv")
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
    parser.add_argument("--models-config", default="configs/models.yaml")
    parser.add_argument("--evaluation-config", default="configs/evaluation.yaml")
    parser.add_argument("--n-jobs", type=int, default=None)
    parser.add_argument("--experiment-name", default=None)
    parser.add_argument("--artifact-location", default=None)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--max-length", type=int, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    import yaml

    models_config = yaml.safe_load(Path(args.models_config).read_text(encoding="utf-8")) or {}
    evaluation_config = yaml.safe_load(Path(args.evaluation_config).read_text(encoding="utf-8")) or {}
    model_config = models_config.get("classical", {})
    search_config = models_config.get("search", {})
    evaluation_search = evaluation_config.get("search", {})
    seed = config.seed if args.seed is None else args.seed
    frame = pd.read_csv(args.train)
    if "content" not in frame or "label" not in frame:
        raise ValueError("Training CSV must contain content and label columns")
    if args.model in {"lstm", "bert"}:
        validation = pd.read_csv(args.validation)
        if "content" not in validation or "label" not in validation:
            raise ValueError("Validation CSV must contain content and label columns")
        if args.model == "lstm":
            _train_lstm_path(frame, validation, args, seed, models_config)
        else:
            _train_bert_path(frame, validation, args, models_config)
        print(json.dumps({"model": args.model, "output": args.output, "rows": len(frame), "validation_rows": len(validation)}, indent=2))
        return

    tfidf_config = config.values["text"]["tfidf"]
    tfidf = TfidfTextPipeline(
        ngram_range=tuple(tfidf_config["ngram_range"]), min_df=tfidf_config["min_df"],
        max_df=tfidf_config["max_df"], max_features=tfidf_config["max_features"],
        sublinear_tf=tfidf_config["sublinear_tf"],
    )
    X_train = tfidf.fit_transform(frame["content"].fillna(""))
    y_train = frame["label"].astype(int).to_numpy()
    feature_transformer = None
    if args.model == "unsupervised":
        from src.features.unsupervised_features import UnsupervisedFeatureAugmenter

        feature_transformer = UnsupervisedFeatureAugmenter(n_clusters=2, random_state=seed)
        X_train = feature_transformer.fit_transform(X_train)
        model = build_logistic_model("l2", random_state=seed)
    else:
        model = select_model(args.model, seed, y_train)
    args.seed = seed
    args.model_config = model_config
    search_type = args.search_type if args.search_type != "none" else str(search_config.get("default_type", evaluation_search.get("default_method", "none")))
    if args.n_iter == 20:
        args.n_iter = int(search_config.get("random_iterations", evaluation_search.get("random_iterations", args.n_iter)))
    if args.cv_folds == 5:
        args.cv_folds = int(search_config.get("cv_folds", evaluation_config.get("cross_validation", {}).get("folds", args.cv_folds)))
    if args.scoring == "average_precision":
        args.scoring = str(search_config.get("scoring", evaluation_search.get("scoring", args.scoring)))
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
                            "model": PackagedTextModel(tfidf, fitted_model, feature_transformer=feature_transformer),

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
