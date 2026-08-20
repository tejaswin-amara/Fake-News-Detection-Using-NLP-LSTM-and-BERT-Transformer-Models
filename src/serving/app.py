"""FastAPI serving boundary for packaged fake-news models.

Compliant with M1/CO1 and M6/CO6. References SRC-008, SRC-009, SRC-030,
SRC-031, and SRC-034. Native packaged preprocessing is authoritative unless an
explicitly parity-verified ONNX serving adapter is configured.
"""

from __future__ import annotations

import os
import platform
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from src.monitoring.drift import (
    build_retraining_signal,
    monitor_features,
    monitor_prediction_probabilities,
    monitor_text_batch,
)
from src.serving.export import load_native_artifact


class PredictionRequest(BaseModel):
    title: str = Field(default="", max_length=20_000)
    text: str = Field(..., min_length=1, max_length=50_000)

    def content(self) -> str:
        content = f"{self.title.strip()}\n{self.text.strip()}".strip()
        if not content:
            raise ValueError("text must contain non-whitespace content")
        return content


class BatchPredictionRequest(BaseModel):
    requests: list[PredictionRequest] = Field(..., min_length=1, max_length=64)


class DriftRequest(BaseModel):
    reference: dict[str, list[float]] | None = Field(default=None, min_length=1)
    current: dict[str, list[float]] | None = Field(default=None, min_length=1)
    reference_texts: list[str] | None = Field(default=None, max_length=10_000)
    current_texts: list[str] | None = Field(default=None, max_length=10_000)
    reference_probabilities: list[float] | None = Field(default=None, max_length=10_000)
    current_probabilities: list[float] | None = Field(default=None, max_length=10_000)
    baseline_revision: str = Field(default="unknown", max_length=200)
    window_id: str = Field(default="request", max_length=200)
    ks_alpha: float = Field(default=0.05, gt=0.0, lt=1.0)
    psi_threshold: float = Field(default=0.20, ge=0.0)
    oov_threshold: float = Field(default=0.20, ge=0.0, le=1.0)
    length_threshold: float = Field(default=0.20, ge=0.0)


class PredictionResponse(BaseModel):
    label: int = Field(..., ge=0, le=1)
    label_name: str
    probability_real: float = Field(..., ge=0.0, le=1.0)
    probability_fake: float = Field(..., ge=0.0, le=1.0)
    model_name: str
    artifact_version: str
    raw_probability_fake: float | None = Field(default=None, ge=0.0, le=1.0)
    calibrated_probability_fake: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence_interval_low: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence_interval_high: float | None = Field(default=None, ge=0.0, le=1.0)
    calibration_status: str = "not_available"
    serving_mode: str = "native"


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]
    count: int
    model_name: str
    artifact_version: str


class ModelService:
    def __init__(self, artifact_path: str | Path | None = None) -> None:
        self.artifact_path = Path(artifact_path or os.getenv("MODEL_ARTIFACT", "artifacts/models/logistic_l2.joblib"))
        self.onnx_path = Path(os.getenv("ONNX_MODEL_PATH", "")) if os.getenv("ONNX_MODEL_PATH") else None
        self.serving_mode = os.getenv("SERVING_MODE", "native")
        self.model: Any | None = None
        self.metadata: dict[str, Any] = {}
        self.error: str | None = None
        self.loaded_at: str | None = None
        self._load()

    def _load(self) -> None:
        if not self.artifact_path.exists():
            self.error = f"Model artifact not found: {self.artifact_path}"
            return
        try:
            artifact = load_native_artifact(self.artifact_path)
            self.model = artifact["model"]
            self.metadata = artifact.get("metadata", {})
            self.metadata.setdefault("serving_mode", self.serving_mode)
            self.metadata.setdefault("onnx_path", str(self.onnx_path) if self.onnx_path else None)
            self.error = None
            self.loaded_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        except Exception as exc:
            self.error = f"Model artifact failed to load: {exc}"

    @property
    def ready(self) -> bool:
        return self.model is not None and hasattr(self.model, "predict_proba")

    def diagnostics(self) -> dict[str, Any]:
        return {
            "model_ready": self.ready,
            "artifact_path": str(self.artifact_path),
            "onnx_path": str(self.onnx_path) if self.onnx_path else None,
            "model_name": self.metadata.get("model_name", "unknown"),
            "artifact_version": self.metadata.get("artifact_version", self.metadata.get("created_at", "unknown")),
            "serving_mode": self.metadata.get("serving_mode", self.serving_mode),
            "calibration_status": self.metadata.get("calibration_status", "not_available"),
            "loaded_at": self.loaded_at,
            "python": platform.python_version(),
            "error": self.error,
        }

    def predict(self, requests: list[PredictionRequest]) -> list[PredictionResponse]:
        if not self.ready:
            raise RuntimeError(self.error or "Model is not ready")
        texts = [request.content() for request in requests]
        started = time.perf_counter()
        try:
            probabilities = self.model.predict_proba(texts)
        except Exception:
            probabilities = self.model.predict_proba([[text] for text in texts])
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        model_probabilities = probabilities[:, 1]
        model_name = str(self.metadata.get("model_name", "unknown"))
        artifact_version = str(self.metadata.get("artifact_version", self.metadata.get("created_at", "unknown")))
        calibration_status = str(self.metadata.get("calibration_status", "not_available"))
        interval = self.metadata.get("confidence_interval")
        responses: list[PredictionResponse] = []
        for probability_fake in model_probabilities:
            raw_probability = float(min(1.0, max(0.0, probability_fake)))
            calibrated_probability = raw_probability
            label = int(calibrated_probability >= 0.5)
            low = interval.get("low") if isinstance(interval, dict) else None
            high = interval.get("high") if isinstance(interval, dict) else None
            response = PredictionResponse(
                label=label,
                label_name="fake" if label else "real",
                probability_real=1.0 - calibrated_probability,
                probability_fake=calibrated_probability,
                model_name=model_name,
                artifact_version=artifact_version,
                raw_probability_fake=raw_probability,
                calibrated_probability_fake=calibrated_probability,
                confidence_interval_low=low,
                confidence_interval_high=high,
                calibration_status=calibration_status,
                serving_mode=str(self.metadata.get("serving_mode", self.serving_mode)),
            )
            response.__dict__["_inference_latency_ms"] = elapsed_ms
            responses.append(response)
        return responses


def _enrich_prediction(prediction: PredictionResponse) -> PredictionResponse:
    data = prediction.model_dump()
    raw = data.get("raw_probability_fake")
    calibrated = data.get("calibrated_probability_fake")
    data["raw_probability_fake"] = data["probability_fake"] if raw is None else raw
    data["calibrated_probability_fake"] = data["probability_fake"] if calibrated is None else calibrated
    return PredictionResponse(**data)


def _service_diagnostics(service: Any) -> dict[str, Any]:
    if hasattr(service, "diagnostics"):
        return service.diagnostics()
    return {
        "model_ready": bool(getattr(service, "ready", False)),
        "artifact_path": str(getattr(service, "artifact_path", "unknown")),
        "model_name": "unknown",
        "artifact_version": "unknown",
        "serving_mode": "native",
        "calibration_status": "not_available",
        "error": getattr(service, "error", None),
    }


def create_app(service: ModelService | None = None) -> FastAPI:
    model_service = service or ModelService()
    application = FastAPI(title="Fake News Detection API", version="0.2.0")

    @application.middleware("http")
    async def latency_header(request: Request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - started) * 1000:.3f}"
        return response

    @application.get("/health")
    def health() -> dict[str, Any]:
        diagnostics = _service_diagnostics(model_service)
        diagnostics["status"] = "ready" if model_service.ready else "degraded"
        return diagnostics

    @application.get("/ready")
    def ready() -> dict[str, Any]:
        if not model_service.ready:
            raise HTTPException(status_code=503, detail=_service_diagnostics(model_service))
        return {"status": "ready", **_service_diagnostics(model_service)}

    @application.post("/monitoring/drift")
    def monitoring_drift(request: DriftRequest) -> dict[str, Any]:
        try:
            reports: dict[str, Any] = {"baseline_revision": request.baseline_revision, "window_id": request.window_id}
            drifted: list[str] = []
            if request.reference is not None and request.current is not None:
                numeric = monitor_features(request.reference, request.current, ks_alpha=request.ks_alpha, psi_threshold=request.psi_threshold)
                reports["numeric"] = numeric
                reports.update(numeric)
                if numeric["drift_detected"]:
                    drifted.extend(name for name, detail in numeric["features"].items() if detail["ks"]["drift_detected"] or detail["psi_drift_detected"])
            if request.reference_probabilities is not None and request.current_probabilities is not None:
                probability = monitor_prediction_probabilities(request.reference_probabilities, request.current_probabilities, psi_threshold=request.psi_threshold)
                reports["probability"] = probability
                if probability["drift_detected"]:
                    drifted.append("prediction_probability")
            if request.reference_texts is not None and request.current_texts is not None:
                text = monitor_text_batch(request.reference_texts, request.current_texts, oov_threshold=request.oov_threshold, length_threshold=request.length_threshold)
                reports["text"] = text
                if text["drift_detected"]:
                    drifted.extend(text["drifted_features"])
            if not reports.keys() - {"baseline_revision", "window_id"}:
                raise ValueError("Provide numeric, probability, or text reference/current data")
            reports["drifted_features"] = sorted(set(drifted))
            reports["drift_detected"] = bool(drifted)
            reports["retraining_signal"] = build_retraining_signal(reports, baseline_revision=request.baseline_revision, window_id=request.window_id)
            return reports
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"Drift monitoring failed: {exc}") from exc

    @application.post("/predict", response_model=PredictionResponse)
    def predict(request: PredictionRequest) -> PredictionResponse:
        try:
            return _enrich_prediction(model_service.predict([request])[0])
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail=f"Prediction failed: {exc}") from exc

    @application.post("/predict/batch", response_model=BatchPredictionResponse)
    def predict_batch(request: BatchPredictionRequest) -> BatchPredictionResponse:
        try:
            predictions = [_enrich_prediction(prediction) for prediction in model_service.predict(request.requests)]
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail=f"Batch prediction failed: {exc}") from exc
        model_name = predictions[0].model_name if predictions else "unknown"
        artifact_version = predictions[0].artifact_version if predictions else "unknown"
        return BatchPredictionResponse(predictions=predictions, count=len(predictions), model_name=model_name, artifact_version=artifact_version)

    return application


app = create_app()
