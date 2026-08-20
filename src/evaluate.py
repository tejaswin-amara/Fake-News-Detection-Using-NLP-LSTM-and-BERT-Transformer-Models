"""Command-line evaluation for a packaged model on a held-out split."""

from __future__ import annotations

import argparse
import json

import joblib
import pandas as pd

from src.evaluation.metrics import evaluate_with_macro_weighted, save_metric_result


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a packaged fake-news model")
    parser.add_argument("--test", default="data/processed/test.csv")
    parser.add_argument("--artifact", default="artifacts/models/logistic_l2.joblib")
    parser.add_argument("--output", default="reports/evaluation.json")
    args = parser.parse_args()

    frame = pd.read_csv(args.test)
    artifact = joblib.load(args.artifact)
    model = artifact["model"] if isinstance(artifact, dict) else artifact
    if not hasattr(model, "predict_proba"):
        raise TypeError("Packaged artifact must expose predict_proba")
    probabilities = model.predict_proba(frame["content"].fillna("").tolist())
    result = evaluate_with_macro_weighted(frame["label"].astype(int).to_numpy(), probabilities)
    result["artifact"] = str(args.artifact)
    result["test_rows"] = int(len(frame))
    save_metric_result(result, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
