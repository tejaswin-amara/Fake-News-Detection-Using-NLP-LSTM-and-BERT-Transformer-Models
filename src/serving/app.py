"""FastAPI serving boundary for packaged fake-news models.

Compliant with M1/CO1 and M6/CO6. References SRC-008, SRC-009, SRC-030, and
SRC-031 in docs/sources.md. The loaded artifact must contain the exact training
preprocessing pipeline to prevent training-serving skew.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from src.monitoring.drift import monitor_features
from src.serving.export import load_native_artifact


class PredictionRequest(BaseModel):
    title: str = Field(default="", max_length=20_000)
    text: str = Field(..., min_length=1, max_length=50_000)

    def content(self) -> str:
        return f"{self.title.strip()}\n{self.text.strip()}".strip()


class BatchPredictionRequest(BaseModel):
    requests: list[PredictionRequest] = Field(..., min_length=1, max_length=64)


class DriftRequest(BaseModel):
    reference: dict[str, list[float]] = Field(..., min_length=1)
    current: dict[str, list[float]] = Field(..., min_length=1)
    ks_alpha: float = Field(default=0.05, gt=0.0, lt=1.0)
    psi_threshold: float = Field(default=0.20, ge=0.0)


class PredictionResponse(BaseModel):
    label: int = Field(..., ge=0, le=1)
    label_name: str
    probability_real: float = Field(..., ge=0.0, le=1.0)
    probability_fake: float = Field(..., ge=0.0, le=1.0)
    model_name: str
    artifact_version: str


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]
    count: int
    model_name: str
    artifact_version: str


class ModelService:
    def __init__(self, artifact_path: str | Path | None = None) -> None:
        self.artifact_path = Path(
            artifact_path or os.getenv("MODEL_ARTIFACT", "artifacts/models/logistic_l2.joblib")
        )
        self.model: Any | None = None
        self.metadata: dict[str, Any] = {}
        self.error: str | None = None
        self._load()

    def _load(self) -> None:
        if not self.artifact_path.exists():
            self.error = f"Model artifact not found: {self.artifact_path}"
            return
        try:
            artifact = load_native_artifact(self.artifact_path)
            self.model = artifact["model"]
            self.metadata = artifact.get("metadata", {})
            self.error = None
        except Exception as exc:  # startup should expose a useful health response
            self.error = f"Model artifact failed to load: {exc}"

    @property
    def ready(self) -> bool:
        return self.model is not None

    def predict(self, requests: list[PredictionRequest]) -> list[PredictionResponse]:
        if not self.ready:
            raise RuntimeError(self.error or "Model is not ready")
        texts = [request.content() for request in requests]
        try:
            probabilities = self.model.predict_proba(texts)
        except Exception:
            probabilities = self.model.predict_proba([[text] for text in texts])
        model_probabilities = probabilities[:, 1]
        model_name = str(self.metadata.get("model_name", "unknown"))
        artifact_version = str(
            self.metadata.get("artifact_version", self.metadata.get("created_at", "unknown"))
        )
        responses = []
        for probability_fake in model_probabilities:
            probability_fake = float(min(1.0, max(0.0, probability_fake)))
            label = int(probability_fake >= 0.5)
            responses.append(
                PredictionResponse(
                    label=label,
                    label_name="fake" if label else "real",
                    probability_real=1.0 - probability_fake,
                    probability_fake=probability_fake,
                    model_name=model_name,
                    artifact_version=artifact_version,
                )
            )
        return responses


def create_app(service: ModelService | None = None) -> FastAPI:
    model_service = service or ModelService()
    application = FastAPI(title="Fake News Detection API", version="0.1.0")

    @application.middleware("http")
    async def latency_header(request: Request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - started) * 1000:.3f}"
        return response

    @application.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ready" if model_service.ready else "degraded",
            "model_ready": model_service.ready,
            "artifact_path": str(model_service.artifact_path),
            "error": model_service.error,
        }

    @application.post("/monitoring/drift")
    def monitoring_drift(request: DriftRequest) -> dict[str, Any]:
        try:
            return monitor_features(
                request.reference,
                request.current,
                ks_alpha=request.ks_alpha,
                psi_threshold=request.psi_threshold,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"Drift monitoring failed: {exc}") from exc

    @application.post("/predict", response_model=PredictionResponse)
    def predict(request: PredictionRequest) -> PredictionResponse:
        try:
            return model_service.predict([request])[0]
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Prediction failed: {exc}") from exc

    @application.post("/predict/batch", response_model=BatchPredictionResponse)
    def predict_batch(request: BatchPredictionRequest) -> BatchPredictionResponse:
        try:
            predictions = model_service.predict(request.requests)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Batch prediction failed: {exc}") from exc
        model_name = predictions[0].model_name if predictions else "unknown"
        artifact_version = predictions[0].artifact_version if predictions else "unknown"
        return BatchPredictionResponse(
            predictions=predictions,
            count=len(predictions),
            model_name=model_name,
            artifact_version=artifact_version,
        )

    return application


app = create_app()
