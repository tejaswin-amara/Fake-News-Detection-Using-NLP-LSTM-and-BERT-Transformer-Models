"""Portable model packaging and export helpers.

Compliant with M6/CO6. References SRC-008, SRC-010, SRC-031, and SRC-034 in
`docs/sources.md`. Native artifacts remain the authoritative fallback when an
exporter does not support a model or preprocessing operation.
"""

from __future__ import annotations

import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib


def save_native_artifact(model: Any, path: str | Path, metadata: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "metadata": metadata}, output)
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
        "created_at": datetime.now(UTC).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "packaging_policy": "native artifact is fallback; export must pass conformance tests",
    }


def export_onnx_sklearn(model: Any, output_path: str | Path, sample_features: Any) -> Path:
    try:
        from skl2onnx import convert_sklearn  # type: ignore
        from skl2onnx.common.data_types import FloatTensorType  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install skl2onnx to export sklearn models to ONNX") from exc
    initial_type = [("features", FloatTensorType([None, sample_features.shape[1]]))]
    onnx_model = convert_sklearn(model, initial_types=initial_type)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(onnx_model.SerializeToString())
    return output


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


def write_export_metadata(metadata: dict[str, Any], output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
