"""Portable model packaging, ONNX export, and parity helpers for CO6/M6.

References SRC-008, SRC-010, SRC-031, and SRC-034. Native artifacts remain the
safe fallback when an exporter cannot represent a tokenizer, vectorizer, or
neural operation without changing inference semantics.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save_native_artifact(model: Any, path: str | Path, metadata: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"model": model, "metadata": metadata}
    joblib.dump(payload, output)
    return output


def load_native_artifact(path: str | Path) -> dict[str, Any]:
    artifact = joblib.load(path)
    if not isinstance(artifact, dict) or "model" not in artifact:
        raise ValueError("Native artifact must contain model and metadata keys")
    return artifact


def artifact_metadata(
    model_name: str, feature_schema: dict[str, Any], seed: int = 42
) -> dict[str, Any]:
    return {
        "model_name": model_name,
        "feature_schema": feature_schema,
        "random_seed": seed,
        "artifact_version": datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
        "created_at": datetime.now(UTC).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "serving_mode": "native",
        "calibration_status": "not_available",
        "confidence_interval": None,
        "packaging_policy": "native artifact is fallback; ONNX must pass parity conformance",
    }


def build_package_manifest(
    model_name: str,
    native_path: str | Path,
    metadata: dict[str, Any],
    onnx_path: str | Path | None = None,
    preprocessing_revision: str = "unknown",
    calibration_revision: str | None = None,
) -> dict[str, Any]:
    """Create an auditable manifest for native/ONNX artifacts and preprocessing."""
    manifest = {
        "manifest_version": "1.0",
        "model_name": model_name,
        "artifact_version": metadata.get("artifact_version", metadata.get("created_at", "unknown")),
        "preprocessing_revision": preprocessing_revision,
        "calibration_revision": calibration_revision,
        "feature_schema": metadata.get("feature_schema", {}),
        "label_mapping": metadata.get("feature_schema", {}).get("label_mapping", {"real": 0, "fake": 1}),
        "native_artifact": {"path": str(native_path), "sha256": sha256_file(native_path) if Path(native_path).exists() else None},
        "onnx_artifact": {"path": str(onnx_path), "sha256": sha256_file(onnx_path) if onnx_path and Path(onnx_path).exists() else None} if onnx_path else None,
        "created_at": datetime.now(UTC).isoformat(),
        "runtime": {"python": sys.version, "platform": platform.platform()},
        "source_ids": metadata.get("source_ids", ["SRC-008", "SRC-010", "SRC-031", "SRC-034"]),
    }
    return manifest


def export_onnx_sklearn(model: Any, output_path: str | Path, sample_features: Any) -> Path:
    try:
        from skl2onnx import convert_sklearn  # type: ignore
        from skl2onnx.common.data_types import FloatTensorType  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install skl2onnx to export sklearn models to ONNX") from exc
    features = sample_features.toarray() if hasattr(sample_features, "toarray") else np.asarray(sample_features)
    if features.ndim != 2 or features.shape[1] == 0:
        raise ValueError("sample_features must be a non-empty two-dimensional feature matrix")
    initial_type = [("features", FloatTensorType([None, features.shape[1]]))]
    try:
        onnx_model = convert_sklearn(model, initial_types=initial_type)
    except Exception as exc:
        raise RuntimeError("The selected sklearn model or preprocessing graph is not ONNX-convertible") from exc
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(onnx_model.SerializeToString())
    return output


def onnx_predict_proba(onnx_path: str | Path, features: Any) -> np.ndarray:
    try:
        import onnxruntime as ort  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install onnxruntime to execute ONNX artifacts") from exc
    matrix = features.toarray() if hasattr(features, "toarray") else np.asarray(features)
    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: matrix.astype(np.float32)})
    if len(outputs) < 2:
        raise ValueError("ONNX classifier must expose labels and probability outputs")
    probabilities = outputs[1]
    if isinstance(probabilities, list):
        probabilities = np.asarray([[row.get(0, 0.0), row.get(1, 0.0)] for row in probabilities], dtype=float)
    probabilities = np.asarray(probabilities)
    if probabilities.ndim == 1:
        probabilities = np.column_stack([1.0 - probabilities, probabilities])
    return probabilities.astype(float)


def onnx_parity_report(
    native_probabilities: Any,
    onnx_probabilities: Any,
    epsilon: float = 1e-5,
) -> dict[str, Any]:
    native = np.asarray(native_probabilities, dtype=float)
    onnx = np.asarray(onnx_probabilities, dtype=float)
    if native.shape != onnx.shape:
        return {"passed": False, "shape_match": False, "native_shape": list(native.shape), "onnx_shape": list(onnx.shape), "epsilon": epsilon}
    absolute = np.abs(native - onnx)
    relative = absolute / np.maximum(np.abs(native), 1e-12)
    max_absolute = float(absolute.max(initial=0.0))
    max_relative = float(relative.max(initial=0.0))
    return {
        "passed": bool(max_absolute < epsilon),
        "shape_match": True,
        "native_shape": list(native.shape),
        "onnx_shape": list(onnx.shape),
        "max_absolute_error": max_absolute,
        "max_relative_error": max_relative,
        "epsilon": epsilon,
    }


def assert_onnx_parity(native_probabilities: Any, onnx_probabilities: Any, epsilon: float = 1e-5) -> dict[str, Any]:
    report = onnx_parity_report(native_probabilities, onnx_probabilities, epsilon=epsilon)
    if not report["passed"]:
        raise AssertionError(f"ONNX parity failed: {report}")
    return report


def export_torchscript(model: Any, output_path: str | Path, example_inputs: Any) -> Path:
    try:
        import torch  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install torch to export TorchScript models") from exc
    model.eval()
    scripted = torch.jit.trace(model, example_inputs)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    scripted.save(str(output))
    return output


def write_export_metadata(metadata: dict[str, Any], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    return output
