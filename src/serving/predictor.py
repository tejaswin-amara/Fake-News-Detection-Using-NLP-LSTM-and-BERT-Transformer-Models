"""Typed inference boundaries for native and ONNX packaged text models.

Compliant with M6/CO6. Native preprocessing remains authoritative; ONNX is used
only after export-time probability parity has been verified.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

import numpy as np
from numpy.typing import NDArray

FloatMatrix = NDArray[np.float64]


class TextInferenceModel(Protocol):
    """Common serving contract for packaged text estimators."""

    def predict_proba(self, texts: Iterable[str]) -> FloatMatrix:
        """Return an ``n x 2`` real/fake probability matrix."""


@dataclass(frozen=True)
class OnnxRuntimeConfig:
    """Safe, explicit ONNX Runtime execution settings."""

    providers: tuple[str, ...] = ("CPUExecutionProvider",)
    intra_op_num_threads: int = 1
    inter_op_num_threads: int = 1
    graph_optimization_level: str = "ORT_ENABLE_ALL"
    enable_cpu_mem_arena: bool = True

    def __post_init__(self) -> None:
        if not self.providers:
            raise ValueError("At least one ONNX execution provider is required")
        if self.intra_op_num_threads < 1 or self.inter_op_num_threads < 1:
            raise ValueError("ONNX thread counts must be positive")
        if self.graph_optimization_level not in {"ORT_DISABLE_ALL", "ORT_ENABLE_BASIC", "ORT_ENABLE_EXTENDED", "ORT_ENABLE_ALL"}:
            raise ValueError("Unsupported ONNX graph optimization level")


class PackagedTextModel:
    """Serialized preprocessing-plus-estimator boundary for online inference."""

    def __init__(self, text_pipeline: Any, estimator: Any, feature_transformer: Any | None = None) -> None:
        self.text_pipeline = text_pipeline
        self.estimator = estimator
        self.feature_transformer = feature_transformer

    def _features(self, texts: Sequence[str]) -> Any:
        features = self.text_pipeline.transform(list(texts))
        if self.feature_transformer is not None:
            features = self.feature_transformer.transform(features)
        return features

    def predict_proba(self, texts: Iterable[str]) -> FloatMatrix:
        values = list(texts)
        features = self._features(values)
        probabilities = np.asarray(self.estimator.predict_proba(features), dtype=np.float64)
        return _validate_probability_matrix(probabilities, len(values))

    def predict(self, texts: Iterable[str]) -> NDArray[np.int64]:
        values = list(texts)
        features = self._features(values)
        return np.asarray(self.estimator.predict(features), dtype=np.int64)


class OnnxTextModel:
    """Reusable ONNX Runtime session bound to the packaged training pipeline."""

    def __init__(self, text_pipeline: Any, session: Any) -> None:
        self.text_pipeline = text_pipeline
        self.session = session
        inputs = session.get_inputs()
        if not inputs:
            raise ValueError("ONNX session exposes no input tensor")
        self.input_name = str(inputs[0].name)

    @classmethod
    def from_artifact(
        cls,
        packaged_model: Any,
        onnx_path: str | Path,
        runtime_config: OnnxRuntimeConfig | None = None,
    ) -> OnnxTextModel:
        try:
            import onnxruntime as ort
        except ImportError as exc:
            raise RuntimeError("ONNX serving requires onnxruntime") from exc
        config = runtime_config or OnnxRuntimeConfig()
        session_options = ort.SessionOptions()
        session_options.intra_op_num_threads = config.intra_op_num_threads
        session_options.inter_op_num_threads = config.inter_op_num_threads
        session_options.enable_cpu_mem_arena = config.enable_cpu_mem_arena
        graph_levels = {
            "ORT_DISABLE_ALL": ort.GraphOptimizationLevel.ORT_DISABLE_ALL,
            "ORT_ENABLE_BASIC": ort.GraphOptimizationLevel.ORT_ENABLE_BASIC,
            "ORT_ENABLE_EXTENDED": ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED,
            "ORT_ENABLE_ALL": ort.GraphOptimizationLevel.ORT_ENABLE_ALL,
        }
        session_options.graph_optimization_level = graph_levels[config.graph_optimization_level]
        session = ort.InferenceSession(
            str(onnx_path),
            sess_options=session_options,
            providers=list(config.providers),
        )
        text_pipeline = getattr(packaged_model, "text_pipeline", None)
        if text_pipeline is None:
            raise ValueError("Packaged model does not contain the training text pipeline")
        return cls(text_pipeline, session)

    def predict_proba(self, texts: Iterable[str]) -> FloatMatrix:
        values = list(texts)
        transformed = self.text_pipeline.transform(values)
        dense = transformed.toarray() if hasattr(transformed, "toarray") else transformed
        matrix = np.asarray(dense, dtype=np.float32)
        outputs = self.session.run(None, {self.input_name: matrix})
        if len(outputs) < 2:
            raise RuntimeError("ONNX classifier must expose label and probability outputs")
        probabilities = outputs[1]
        if isinstance(probabilities, list):
            probabilities = np.asarray([[row.get(0, 0.0), row.get(1, 0.0)] for row in probabilities], dtype=np.float64)
        return _validate_probability_matrix(np.asarray(probabilities, dtype=np.float64), len(values))


def _validate_probability_matrix(probabilities: NDArray[Any], expected_rows: int) -> FloatMatrix:
    values = np.asarray(probabilities, dtype=np.float64)
    if values.ndim != 2 or values.shape != (expected_rows, 2):
        raise RuntimeError(f"Probability matrix must have shape ({expected_rows}, 2); got {values.shape}")
    if not np.isfinite(values).all():
        raise RuntimeError("Inference produced non-finite probabilities")
    if np.any(values < -1e-8) or np.any(values > 1.0 + 1e-8):
        raise RuntimeError("Inference produced probabilities outside [0, 1]")
    row_sums = values.sum(axis=1)
    if not np.allclose(row_sums, 1.0, atol=1e-5):
        raise RuntimeError("Inference probabilities do not sum to one")
    return cast(FloatMatrix, np.clip(values, 0.0, 1.0))
