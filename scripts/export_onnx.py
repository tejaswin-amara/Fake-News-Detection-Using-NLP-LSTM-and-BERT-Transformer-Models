"""Export a packaged sklearn estimator and verify native/ONNX probability parity."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import pandas as pd

from src.serving.export import (
    assert_onnx_parity,
    build_package_manifest,
    export_onnx_sklearn,
    onnx_predict_proba,
    write_export_metadata,
)


def _load_artifact(path: Path) -> tuple[Any, dict[str, Any]]:
    payload = joblib.load(path)
    if not isinstance(payload, dict) or "model" not in payload:
        raise ValueError("Native artifact must be a dictionary containing model and metadata")
    return payload["model"], dict(payload.get("metadata", {}))


def export_artifact(
    artifact_path: Path,
    training_path: Path,
    onnx_path: Path,
    manifest_path: Path,
    epsilon: float,
) -> dict[str, Any]:
    model, metadata = _load_artifact(artifact_path)
    manifest: dict[str, Any]
    estimator = getattr(model, "estimator", None)
    pipeline = getattr(model, "text_pipeline", None)
    if estimator is None or pipeline is None or not hasattr(estimator, "predict_proba"):
        manifest = build_package_manifest(
            str(metadata.get("model_name", "unknown")), artifact_path, metadata, onnx_path=None
        )
        manifest.update({"status": "native_only", "reason": "artifact has no compatible sklearn estimator/pipeline"})
        write_export_metadata(manifest, manifest_path)
        return manifest

    frame = pd.read_csv(training_path)
    if "content" not in frame:
        raise ValueError("Training CSV must contain the content column for conformance features")
    features = pipeline.transform(frame["content"].fillna("").tolist())
    native_probabilities = np.asarray(estimator.predict_proba(features), dtype=float)
    try:
        exported = export_onnx_sklearn(estimator, onnx_path, features)
        onnx_probabilities = onnx_predict_proba(exported, features)
        parity = assert_onnx_parity(native_probabilities, onnx_probabilities, epsilon=epsilon)
        manifest = build_package_manifest(
            str(metadata.get("model_name", "unknown")), artifact_path, metadata, exported,
            preprocessing_revision=str(metadata.get("artifact_version", "unknown")),
        )
        manifest.update({"status": "onnx_verified", "parity": parity, "conformance_rows": int(len(frame))})
    except (RuntimeError, ValueError) as exc:
        manifest = build_package_manifest(
            str(metadata.get("model_name", "unknown")), artifact_path, metadata, onnx_path=None,
            preprocessing_revision=str(metadata.get("artifact_version", "unknown")),
        )
        manifest.update({"status": "native_only", "reason": str(exc), "conformance_rows": int(len(frame))})
        if onnx_path.exists():
            onnx_path.unlink()
    write_export_metadata(manifest, manifest_path)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a trained fake-news model to ONNX when parity is verified")
    parser.add_argument("--artifact", type=Path, default=Path("artifacts/models/logistic_l2.joblib"))
    parser.add_argument("--training", type=Path, default=Path("data/processed/train.csv"))
    parser.add_argument("--onnx", type=Path, default=Path("artifacts/models/logistic_l2.onnx"))
    parser.add_argument("--manifest", type=Path, default=Path("artifacts/models/package_manifest.json"))
    parser.add_argument("--epsilon", type=float, default=9e-6)
    args = parser.parse_args()
    if args.epsilon >= 1e-5:
        parser.error("--epsilon must be strictly less than 1e-5")
    result = export_artifact(args.artifact, args.training, args.onnx, args.manifest, args.epsilon)
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
