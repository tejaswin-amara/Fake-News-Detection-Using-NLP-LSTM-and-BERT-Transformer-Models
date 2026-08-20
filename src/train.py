"""Command-line training entry point for the reproducible classical path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.config import load_config
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


def select_model(name: str, seed: int):
    if name == "logistic_l1":
        return build_logistic_model("l1", random_state=seed)
    if name == "logistic_l2":
        return build_logistic_model("l2", random_state=seed)
    if name == "logistic_elasticnet":
        return build_logistic_model("elasticnet", random_state=seed)
    if name == "decision_tree":
        return build_decision_tree(ccp_alpha=0.001, random_state=seed)
    if name == "random_forest":
        return build_random_forest(random_state=seed)
    if name == "xgboost":
        return build_xgboost(random_state=seed)
    if name == "lightgbm":
        return build_lightgbm(random_state=seed)
    raise ValueError(f"Unknown model: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a classical fake-news model")
    parser.add_argument("--train", default="data/processed/train.csv")
    parser.add_argument("--output", default="artifacts/models/logistic_l2.joblib")
    parser.add_argument("--model", default="logistic_l2")
    parser.add_argument("--config", default="configs/default.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    frame = pd.read_csv(args.train)
    if "content" not in frame or "label" not in frame:
        raise ValueError("Training CSV must contain content and label columns")
    tfidf = TfidfTextPipeline(
        ngram_range=tuple(config.values["text"]["tfidf"]["ngram_range"]),
        min_df=config.values["text"]["tfidf"]["min_df"],
        max_df=config.values["text"]["tfidf"]["max_df"],
        max_features=config.values["text"]["tfidf"]["max_features"],
        sublinear_tf=config.values["text"]["tfidf"]["sublinear_tf"],
    )
    X_train = tfidf.fit_transform(frame["content"].fillna(""))
    y_train = frame["label"].astype(int).to_numpy()
    model = select_model(args.model, config.seed)
    model.fit(X_train, y_train)
    artifact = {
        "model": PackagedTextModel(tfidf, model),
        "metadata": artifact_metadata(
            args.model,
            {
                "representation": "tfidf",
                "feature_count": int(X_train.shape[1]),
                "label_mapping": {"real": 0, "fake": 1},
            },
            config.seed,
        ),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    import joblib

    joblib.dump(artifact, output)
    print(
        json.dumps(
            {
                "model": args.model,
                "output": str(output),
                "rows": len(frame),
                "features": X_train.shape[1],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
