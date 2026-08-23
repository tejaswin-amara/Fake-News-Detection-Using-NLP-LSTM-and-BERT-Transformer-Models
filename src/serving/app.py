"""Hardened FastAPI serving boundary for packaged fake-news models.

Compliant with M1/CO1 and M6/CO6. References SRC-008, SRC-009, SRC-030,
SRC-031, and SRC-034. Native packaged preprocessing is authoritative unless an
explicitly parity-verified ONNX serving adapter is configured.
"""

from __future__ import annotations

import asyncio
import math
import os
import platform
import re
import threading
import time
import uuid
from collections import deque
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Protocol, cast

import numpy as np
import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from starlette.concurrency import run_in_threadpool

from src.config import bind_request_id, configure_logging, reset_request_id
from src.monitoring.drift import (
    build_retraining_signal,
    monitor_features,
    monitor_prediction_probabilities,
    monitor_text_batch,
)
from src.monitoring.jobs import DriftJobManager
from src.serving.export import load_verified_native_artifact
from src.serving.predictor import (
    OnnxRuntimeConfig,
    OnnxTextModel,
    TextInferenceModel,
    warmup_text_model,
)
from src.serving.rate_limiter import RedisRateLimiter, redis_is_configured

logger = structlog.get_logger(__name__)

_CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_REQUEST_ID_SAFE = re.compile(r"[^A-Za-z0-9._:-]")
_SAFE_TEXT_MAX = 50_000
_SAFE_BATCH_MAX = 64
_JSON_REQUEST_PATHS = frozenset({"/predict", "/predict/batch", "/monitoring/drift"})
_PUBLIC_DIAGNOSTIC_FIELDS = (
    "model_ready",
    "model_name",
    "artifact_version",
    "serving_mode",
    "calibration_status",
)

HTTP_REQUEST_LATENCY = Histogram(
    "fake_news_http_request_latency_seconds",
    "HTTP request latency for the fake-news detection service.",
    ("method", "route", "status"),
)
INFERENCE_LATENCY = Histogram(
    "fake_news_inference_latency_seconds",
    "Inference latency for native and ONNX prediction paths.",
    ("endpoint", "serving_mode"),
)
INFERENCE_QUEUE_DEPTH = Gauge(
    "fake_news_inference_queue_depth",
    "Requests waiting for an inference permit; bounded admission rejects rather than queues when exhausted.",
)
DRIFT_QUEUE_DEPTH = Gauge(
    "fake_news_drift_queue_depth",
    "Current number of queued drift-monitoring jobs.",
)
RATE_LIMITER_REJECTIONS = Counter(
    "fake_news_rate_limiter_rejections",
    "Rejected requests by bounded admission-control reason.",
    ("reason",),
)
DRIFT_MONITORING_ERRORS = Counter(
    "fake_news_drift_monitoring_errors",
    "Drift-monitoring jobs that failed during processing.",
)


def _metrics_route(path: str) -> str:
    if path.startswith("/monitoring/drift/"):
        return "/monitoring/drift/{job_id}"
    return path


def _finalize_http_response(request: Request, response: Response, request_id: str) -> Response:
    response.headers["X-Request-ID"] = request_id
    response.headers.setdefault("Cache-Control", "no-store")
    response.headers.setdefault("Content-Security-Policy", "frame-ancestors 'none'")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    started = getattr(request.state, "started", time.perf_counter())
    elapsed = time.perf_counter() - started
    response.headers["X-Process-Time-Ms"] = f"{elapsed * 1000:.3f}"
    HTTP_REQUEST_LATENCY.labels(
        request.method, _metrics_route(request.url.path), str(response.status_code)
    ).observe(elapsed)
    return response


def _validate_text_value(value: str, field_name: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    if len(value) > max_length:
        raise ValueError(f"{field_name} exceeds the maximum length")
    if _CONTROL_CHARACTERS.search(value):
        raise ValueError(f"{field_name} contains disallowed control characters")
    return value


class PredictionRequest(BaseModel):
    """Strict single-article request with no unknown JSON fields."""

    model_config = ConfigDict(extra="forbid", strict=True)

    title: str = Field(default="", max_length=20_000)
    text: str = Field(..., min_length=1, max_length=_SAFE_TEXT_MAX)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return _validate_text_value(value, "title", 20_000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return _validate_text_value(value, "text", _SAFE_TEXT_MAX)

    def content(self) -> str:
        content = f"{self.title.strip()}\n{self.text.strip()}".strip()
        if not content:
            raise ValueError("text must contain non-whitespace content")
        return content


class BatchPredictionRequest(BaseModel):
    """Strict bounded batch request."""

    model_config = ConfigDict(extra="forbid", strict=True)
    requests: list[PredictionRequest] = Field(..., min_length=1, max_length=_SAFE_BATCH_MAX)


class DriftRequest(BaseModel):
    """Strict drift request accepting exactly one complete reference/current pair."""

    model_config = ConfigDict(extra="forbid", strict=True)

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

    @field_validator("baseline_revision", "window_id")
    @classmethod
    def validate_identifiers(cls, value: str) -> str:
        return _validate_text_value(value, "identifier", 200)

    @field_validator("reference", "current")
    @classmethod
    def validate_numeric_mapping(cls, value: dict[str, list[float]] | None) -> dict[str, list[float]] | None:
        if value is None:
            return None
        for name, values in value.items():
            _validate_text_value(name, "feature name", 200)
            if not 2 <= len(values) <= 10_000:
                raise ValueError("numeric drift arrays must contain between 2 and 10000 values")
            if not all(math.isfinite(number) for number in values):
                raise ValueError("numeric drift arrays must contain only finite values")
        return value

    @field_validator("reference_probabilities", "current_probabilities")
    @classmethod
    def validate_probabilities(cls, value: list[float] | None) -> list[float] | None:
        if value is None:
            return None
        if not 2 <= len(value) <= 10_000:
            raise ValueError("probability arrays must contain between 2 and 10000 values")
        if not all(math.isfinite(number) and 0.0 <= number <= 1.0 for number in value):
            raise ValueError("probabilities must be finite and lie in [0, 1]")
        return value

    @field_validator("reference_texts", "current_texts")
    @classmethod
    def validate_text_arrays(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        if len(value) < 2:
            raise ValueError("text drift requires at least two texts")
        for text in value:
            _validate_text_value(text, "monitored text", _SAFE_TEXT_MAX)
        return value

    @model_validator(mode="after")
    def validate_complete_pair(self) -> DriftRequest:
        groups = (
            (self.reference, self.current),
            (self.reference_texts, self.current_texts),
            (self.reference_probabilities, self.current_probabilities),
        )
        if not any(left is not None and right is not None for left, right in groups):
            raise ValueError("Provide one complete numeric, probability, or text reference/current pair")
        if any((left is None) != (right is None) for left, right in groups):
            raise ValueError("Each drift reference/current pair must be provided together")
        return self


class PredictionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    low_signal: bool = False


class BatchPredictionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    predictions: list[PredictionResponse]
    count: int
    model_name: str
    artifact_version: str


class ServingService(Protocol):
    """Structural service contract used by the FastAPI factory and tests."""

    ready: bool
    error: str | None

    def predict(self, requests: list[PredictionRequest]) -> list[PredictionResponse]:
        """Predict for an already validated bounded request list."""


class RateLimiter:
    """Thread-safe bounded fixed-window limiter for a single service instance."""

    def __init__(self, limit: int = 120, window_seconds: float = 60.0, max_clients: int = 10_000) -> None:
        if limit < 1 or window_seconds <= 0.0 or max_clients < 1:
            raise ValueError("rate limiter settings must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_clients = max_clients
        self._events: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def check(self, client_key: str, now: float | None = None) -> tuple[bool, int]:
        current = time.monotonic() if now is None else now
        with self._lock:
            events = self._events.setdefault(client_key, deque())
            cutoff = current - self.window_seconds
            while events and events[0] <= cutoff:
                events.popleft()
            if len(self._events) > self.max_clients:
                oldest_key = min(self._events, key=lambda key: self._events[key][-1] if self._events[key] else current)
                if oldest_key != client_key:
                    self._events.pop(oldest_key, None)
            if len(events) >= self.limit:
                retry_after = max(1, int(math.ceil(events[0] + self.window_seconds - current)))
                return False, retry_after
            events.append(current)
            return True, 0

    async def check_async(self, client_key: str) -> tuple[bool, int]:
        return self.check(client_key)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value is None else int(value)


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value is None else float(value)


def _env_csv(name: str, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return tuple(item.strip() for item in value.split(",") if item.strip())


class ModelService:
    """Load the packaged model/session once and reuse it for every request."""

    def __init__(self, artifact_path: str | Path | None = None) -> None:
        raw_artifact: str | Path = artifact_path if artifact_path is not None else os.getenv("MODEL_ARTIFACT", "artifacts/models/logistic_l2.joblib")
        self.artifact_path = Path(raw_artifact)
        raw_onnx = os.getenv("ONNX_MODEL_PATH", "")
        self.onnx_path = Path(raw_onnx) if raw_onnx else None
        self.serving_mode = os.getenv("SERVING_MODE", "native").strip().lower()
        self.model: TextInferenceModel | None = None
        self.metadata: dict[str, Any] = {}
        self.error: str | None = None
        self.loaded_at: str | None = None
        self._loaded = False

    def _runtime_config(self) -> OnnxRuntimeConfig:
        return OnnxRuntimeConfig(
            providers=_env_csv("ONNX_EXECUTION_PROVIDERS", ("CPUExecutionProvider",)),
            intra_op_num_threads=_env_int("ONNX_INTRA_OP_THREADS", 1),
            inter_op_num_threads=_env_int("ONNX_INTER_OP_THREADS", 1),
            graph_optimization_level=os.getenv("ONNX_GRAPH_OPTIMIZATION", "ORT_ENABLE_ALL"),
            enable_cpu_mem_arena=_env_bool("ONNX_CPU_MEM_ARENA", True),
        )

    def load(self) -> None:
        if self._loaded:
            return
        self._load()
        self._loaded = True

    def _load(self) -> None:
        if not self.artifact_path.exists():
            self.error = f"Model artifact not found: {self.artifact_path}"
            return
        try:
            manifest_path = os.getenv("PACKAGE_MANIFEST", "")
            public_key = os.getenv("ARTIFACT_PUBLIC_KEY_B64", "")
            require_signature = _env_bool("REQUIRE_SIGNED_ARTIFACT", True)
            if require_signature:
                if not manifest_path or not public_key:
                    raise ValueError("Signed native serving requires PACKAGE_MANIFEST and ARTIFACT_PUBLIC_KEY_B64")
                artifact = load_verified_native_artifact(self.artifact_path, manifest_path, public_key_b64=public_key, require_signature=True)
            else:
                from src.serving.export import load_native_artifact, sha256_file

                artifact = load_native_artifact(self.artifact_path, os.getenv("MODEL_ARTIFACT_SHA256", sha256_file(self.artifact_path)))
            packaged_model = artifact["model"]
            if not hasattr(packaged_model, "predict_proba"):
                raise TypeError("Packaged artifact does not expose predict_proba")
            self.metadata = dict(artifact.get("metadata", {}))
            if self.serving_mode == "onnx":
                if self.onnx_path is None or not self.onnx_path.exists():
                    raise FileNotFoundError("ONNX serving mode requires an existing ONNX_MODEL_PATH")
                self.model = OnnxTextModel.from_artifact(packaged_model, self.onnx_path, self._runtime_config())
            else:
                self.model = cast(TextInferenceModel, packaged_model)
            self.metadata.setdefault("serving_mode", self.serving_mode)
            self.metadata.setdefault("onnx_path", str(self.onnx_path) if self.onnx_path else None)
            self.error = None
            self.loaded_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        except Exception as exc:
            self.model = None
            self.error = f"Model artifact failed to load: {type(exc).__name__}"

    def close(self) -> None:
        session = getattr(self.model, "session", None)
        close = getattr(session, "close", None)
        if callable(close):
            close()
        self.model = None
        self._loaded = False

    @property
    def ready(self) -> bool:
        return self.model is not None and callable(getattr(self.model, "predict_proba", None))

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
            "onnx_providers": list(_env_csv("ONNX_EXECUTION_PROVIDERS", ("CPUExecutionProvider",))),
            "onnx_intra_op_threads": _env_int("ONNX_INTRA_OP_THREADS", 1),
            "onnx_inter_op_threads": _env_int("ONNX_INTER_OP_THREADS", 1),
            "error": self.error,
        }

    def predict(self, requests: list[PredictionRequest]) -> list[PredictionResponse]:
        if not self.ready or self.model is None:
            raise RuntimeError(self.error or "Model is not ready")
        texts = [request.content() for request in requests]
        low_signal_flags: list[bool] = []
        pipeline = getattr(self.model, "text_pipeline", None)
        if pipeline is not None:
            transformed = pipeline.transform(texts)
            if hasattr(transformed, "getnnz"):
                nonzero = np.asarray(transformed.getnnz(axis=1)).reshape(-1)
            else:
                nonzero = np.count_nonzero(np.asarray(transformed), axis=1)
            low_signal_flags = [int(value) == 0 for value in nonzero.tolist()]
        else:
            low_signal_flags = [not bool(re.search(r"[A-Za-z0-9]", text)) for text in texts]
        probabilities = np.asarray(self.model.predict_proba(texts), dtype=np.float64)
        if probabilities.ndim != 2 or probabilities.shape != (len(texts), 2):
            raise RuntimeError("Model returned an invalid probability matrix")
        if not np.isfinite(probabilities).all():
            raise RuntimeError("Model returned non-finite probabilities")
        raw = np.clip(probabilities[:, 1], 0.0, 1.0)
        labels = (raw >= 0.5).astype(np.int8)
        model_name = str(self.metadata.get("model_name", "unknown"))
        artifact_version = str(self.metadata.get("artifact_version", self.metadata.get("created_at", "unknown")))
        calibration_status = str(self.metadata.get("calibration_status", "not_available"))
        interval = self.metadata.get("confidence_interval")
        low = interval.get("low") if isinstance(interval, dict) else None
        high = interval.get("high") if isinstance(interval, dict) else None
        serving_mode = str(self.metadata.get("serving_mode", self.serving_mode))
        return [
            PredictionResponse(
                label=int(label),
                label_name="fake" if label else "real",
                probability_real=float(1.0 - probability_fake),
                probability_fake=float(probability_fake),
                model_name=model_name,
                artifact_version=artifact_version,
                raw_probability_fake=float(probability_fake),
                calibrated_probability_fake=float(probability_fake),
                confidence_interval_low=low,
                confidence_interval_high=high,
                calibration_status=calibration_status,
                serving_mode=serving_mode,
                low_signal=low_signal,
            )
            for label, probability_fake, low_signal in zip(labels.tolist(), raw.tolist(), low_signal_flags, strict=True)
        ]


def _enrich_prediction(prediction: PredictionResponse, text: str | None = None) -> PredictionResponse:
    data = prediction.model_dump()
    raw = data.get("raw_probability_fake")
    calibrated = data.get("calibrated_probability_fake")
    data["raw_probability_fake"] = data["probability_fake"] if raw is None else raw
    data["calibrated_probability_fake"] = data["probability_fake"] if calibrated is None else calibrated
    if text is not None:
        data["low_signal"] = bool(data.get("low_signal", False) or not re.search(r"[A-Za-z0-9]", text))
    return PredictionResponse(**data)


def _service_diagnostics(service: Any) -> dict[str, Any]:
    diagnostics = getattr(service, "diagnostics", None)
    if callable(diagnostics):
        result = diagnostics()
        if isinstance(result, dict):
            return cast(dict[str, Any], result)
    return {
        "model_ready": bool(getattr(service, "ready", False)),
        "artifact_path": str(getattr(service, "artifact_path", "unknown")),
        "model_name": "unknown",
        "artifact_version": "unknown",
        "serving_mode": "native",
        "calibration_status": "not_available",
        "error": getattr(service, "error", None),
    }


def _public_service_diagnostics(service: Any) -> dict[str, Any]:
    """Return readiness metadata without filesystem, runtime, or exception detail."""
    diagnostics = _service_diagnostics(service)
    return {field: diagnostics.get(field) for field in _PUBLIC_DIAGNOSTIC_FIELDS}


def _client_key(request: Request, trusted_proxy_ips: set[str]) -> str:
    host = request.client.host if request.client else "unknown"
    if host in trusted_proxy_ips:
        forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
        if forwarded:
            return forwarded
    return host


def _cors_origins() -> tuple[str, ...]:
    return _env_csv("CORS_ALLOWED_ORIGINS")


def _process_drift_payload(payload: dict[str, Any]) -> dict[str, Any]:
    request = DriftRequest.model_validate(payload)
    reports: dict[str, Any] = {"baseline_revision": request.baseline_revision, "window_id": request.window_id}
    drifted: list[str] = []
    if request.reference is not None and request.current is not None:
        numeric = monitor_features(request.reference, request.current, ks_alpha=request.ks_alpha, psi_threshold=request.psi_threshold)
        reports["numeric"] = numeric
        reports.update(numeric)
        if numeric["drift_detected"]:
            drifted.extend(name for name, detail in numeric["features"].items() if detail["ks"]["drift_detected"] or detail["psi_drift_detected"])
    if request.reference_probabilities is not None and request.current_probabilities is not None:
        probability = monitor_prediction_probabilities(request.reference_probabilities, request.current_probabilities, psi_threshold=request.psi_threshold, ks_alpha=request.ks_alpha)
        reports["probability"] = probability
        if probability["drift_detected"]:
            drifted.append("prediction_probability")
    if request.reference_texts is not None and request.current_texts is not None:
        text = monitor_text_batch(request.reference_texts, request.current_texts, oov_threshold=request.oov_threshold, length_threshold=request.length_threshold, ks_alpha=request.ks_alpha)
        reports["text"] = text
        if text["drift_detected"]:
            drifted.extend(text["drifted_features"])
    reports["drifted_features"] = sorted(set(drifted))
    reports["drift_detected"] = bool(drifted)
    reports["retraining_signal"] = build_retraining_signal(reports, baseline_revision=request.baseline_revision, window_id=request.window_id)
    return reports


def create_app(
    service: ServingService | None = None,
    rate_limiter: RateLimiter | None = None,
) -> FastAPI:
    """Create an app with injectable service/limiter dependencies for safe tests."""
    configure_logging()
    model_service: ServingService = service if service is not None else cast(ServingService, ModelService())
    origins = _cors_origins()
    credentials = _env_bool("CORS_ALLOW_CREDENTIALS", False)
    if credentials and "*" in origins:
        raise ValueError("Wildcard CORS origins cannot be combined with credentials")
    limiter: RateLimiter | RedisRateLimiter | None = rate_limiter
    if limiter is None and redis_is_configured():
        limiter = RedisRateLimiter(
            os.environ["REDIS_URL"],
            _env_int("RATE_LIMIT_REQUESTS", 120),
            _env_float("RATE_LIMIT_WINDOW_SECONDS", 60.0),
            os.getenv("REDIS_RATE_LIMIT_KEY_PREFIX", "fake-news:ratelimit:"),
            _env_int("REDIS_CIRCUIT_FAILURE_THRESHOLD", 3),
            _env_float("REDIS_CIRCUIT_RECOVERY_SECONDS", 30.0),
        )
    if limiter is None:
        limiter = RateLimiter(
            _env_int("RATE_LIMIT_REQUESTS", 120),
            _env_float("RATE_LIMIT_WINDOW_SECONDS", 60.0),
            _env_int("RATE_LIMIT_MAX_CLIENTS", 10_000),
        )
    trusted_proxy_ips = set(_env_csv("TRUSTED_PROXY_IPS"))
    web_concurrency = _env_int("WEB_CONCURRENCY", 1)
    distributed_limiter = os.getenv("DISTRIBUTED_RATE_LIMITER", "").strip()
    if web_concurrency > 1 and not distributed_limiter:
        raise ValueError("WEB_CONCURRENCY>1 requires DISTRIBUTED_RATE_LIMITER configuration")
    max_request_bytes = _env_int("MAX_REQUEST_BYTES", 1_000_000)
    max_inflight_inference = _env_int("MAX_INFLIGHT_INFERENCE", 4)
    if max_inflight_inference < 1:
        raise ValueError("MAX_INFLIGHT_INFERENCE must be positive")
    inference_budget = asyncio.Semaphore(max_inflight_inference)
    drift_jobs = DriftJobManager(
        _process_drift_payload,
        maxsize=_env_int("DRIFT_QUEUE_MAXSIZE", 128),
        workers=_env_int("DRIFT_WORKERS", 2),
        ttl_seconds=_env_int("DRIFT_JOB_TTL_SECONDS", 900),
        on_failure=lambda _error: DRIFT_MONITORING_ERRORS.inc(),
    )
    if max_request_bytes < 1:
        raise ValueError("MAX_REQUEST_BYTES must be positive")

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.model_service = model_service
        application.state.warmup_complete = False
        application.state.warmup_error = None
        await drift_jobs.start()
        load = getattr(model_service, "load", None)
        if callable(load):
            load()
        try:
            if not model_service.ready:
                raise RuntimeError("Model is not ready for warm-up")
            if isinstance(model_service, ModelService) and model_service.model is not None:
                warmup_text_model(model_service.model)
            else:
                warmup_predictions = model_service.predict([PredictionRequest(text="System startup warm-up article.")])
                if len(warmup_predictions) != 1:
                    raise RuntimeError("Warm-up returned an invalid prediction count")
            application.state.warmup_complete = True
        except Exception as exc:
            application.state.warmup_error = type(exc).__name__
            if getattr(model_service, "error", None) is None:
                model_service.error = f"Model warm-up failed: {type(exc).__name__}"
        yield
        close = getattr(model_service, "close", None)
        if callable(close):
            result = close()
            if hasattr(result, "__await__"):
                await result
        await drift_jobs.stop()
        limiter_close = getattr(limiter, "close", None)
        if callable(limiter_close):
            result = limiter_close()
            if hasattr(result, "__await__"):
                await result

    application = FastAPI(
        title="Fake News Detection API",
        description=(
            "Bounded text-classification and drift-monitoring API. The OpenAPI contract contains "
            "metadata only: clients must not place credentials or sensitive article text in public logs, issues, or examples."
        ),
        version="0.3.0",
        openapi_tags=[
            {"name": "service", "description": "Health, readiness, and metrics endpoints."},
            {"name": "prediction", "description": "Bounded inference endpoints."},
            {"name": "monitoring", "description": "Asynchronous metadata and drift monitoring endpoints."},
        ],
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(origins),
        allow_credentials=credentials,
        allow_methods=list(_env_csv("CORS_ALLOWED_METHODS", ("GET", "POST", "OPTIONS"))),
        allow_headers=list(_env_csv("CORS_ALLOWED_HEADERS", ("Content-Type", "X-Request-ID"))),
        max_age=600,
    )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        del exc
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        return JSONResponse(status_code=422, content={"detail": "Request validation failed", "request_id": request_id})

    @application.middleware("http")
    async def request_security_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        raw_request_id = request.headers.get("x-request-id", "")
        request_id = _REQUEST_ID_SAFE.sub("", raw_request_id)[:128] or uuid.uuid4().hex
        request_context = bind_request_id(request_id)
        logger.info("request_started", method=request.method, route=_metrics_route(request.url.path))
        try:
            content_length = request.headers.get("content-length")
            if content_length is not None:
                try:
                    oversized = int(content_length) > max_request_bytes
                except ValueError:
                    oversized = True
                if oversized:
                    response = _finalize_http_response(
                        request,
                        JSONResponse(
                            status_code=413,
                            content={"detail": "Request body exceeds the configured limit", "request_id": request_id},
                        ),
                        request_id,
                    )
                    logger.warning("request_rejected", reason="request_too_large", status_code=413)
                    return response
            if request.method == "POST" and request.url.path in _JSON_REQUEST_PATHS:
                media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
                if media_type != "application/json":
                    response = _finalize_http_response(
                        request,
                        JSONResponse(
                            status_code=415,
                            content={"detail": "This endpoint requires application/json", "request_id": request_id},
                        ),
                        request_id,
                    )
                    logger.warning("request_rejected", reason="unsupported_media_type", status_code=415)
                    return response
            if request.method != "OPTIONS" and request.url.path not in {"/health", "/ready", "/metrics"}:
                allowed, retry_after = await limiter.check_async(_client_key(request, trusted_proxy_ips))
                if not allowed:
                    RATE_LIMITER_REJECTIONS.labels(reason="rate_limit").inc()
                    rejected_response = JSONResponse(
                        status_code=429,
                        content={"detail": "Rate limit exceeded", "request_id": request_id},
                        headers={"Retry-After": str(retry_after)},
                    )
                    logger.warning("request_rejected", reason="rate_limit", status_code=429)
                    return _finalize_http_response(request, rejected_response, request_id)
            response = await call_next(request)
            finalized = _finalize_http_response(request, response, request_id)
            logger.info(
                "request_completed",
                status_code=response.status_code,
                latency_ms=round(float(response.headers.get("X-Process-Time-Ms", "0")), 3),
            )
            return finalized
        except Exception:
            logger.exception("request_failed")
            raise
        finally:
            reset_request_id(request_context)

    @application.middleware("http")
    async def timing_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request.state.started = time.perf_counter()
        return await call_next(request)

    @application.get("/metrics", tags=["service"], include_in_schema=False)
    def metrics() -> Response:
        # Inference uses immediate 429 admission control rather than an unbounded
        # backlog, so no request is ever kept waiting for an inference permit.
        INFERENCE_QUEUE_DEPTH.set(0.0)
        DRIFT_QUEUE_DEPTH.set(float(drift_jobs.queue.qsize()))
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @application.get("/health", tags=["service"])
    def health() -> dict[str, Any]:
        diagnostics = _public_service_diagnostics(model_service)
        warmup_complete = bool(getattr(application.state, "warmup_complete", model_service.ready))
        diagnostics["warmup_complete"] = warmup_complete
        diagnostics["warmup_error"] = getattr(application.state, "warmup_error", None)
        diagnostics["status"] = "ready" if model_service.ready and warmup_complete else "degraded"
        return diagnostics

    @application.get("/ready", tags=["service"])
    def ready() -> dict[str, Any]:
        warmup_complete = bool(getattr(application.state, "warmup_complete", model_service.ready))
        if not model_service.ready or not warmup_complete:
            raise HTTPException(status_code=503, detail="Serving readiness check failed")
        return {"status": "ready", "warmup_complete": True, **_public_service_diagnostics(model_service)}

    @application.post("/monitoring/drift", status_code=202, tags=["monitoring"])
    async def monitoring_drift(request: DriftRequest) -> dict[str, Any]:
        """Enqueue bounded drift-monitoring work without blocking the request."""
        try:
            job_id = await drift_jobs.submit(request.model_dump())
        except OverflowError as exc:
            RATE_LIMITER_REJECTIONS.labels(reason="drift_queue").inc()
            logger.warning("drift_job_rejected", reason="queue_full", status_code=429)
            raise HTTPException(
                status_code=429,
                detail="Drift monitoring queue is full; retry later",
                headers={"Retry-After": "5"},
            ) from exc
        except RuntimeError as exc:
            logger.error("drift_job_unavailable", status_code=503)
            raise HTTPException(status_code=503, detail="Drift job queue unavailable") from exc
        logger.info("drift_job_enqueued", job_id=job_id)
        return {"job_id": job_id, "status": "queued"}

    @application.get("/monitoring/drift/{job_id}", tags=["monitoring"])
    async def monitoring_drift_status(job_id: str) -> dict[str, Any]:
        status = drift_jobs.status(job_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Drift job not found")
        return status

    async def bounded_predict(requests: list[PredictionRequest]) -> list[PredictionResponse]:
        if inference_budget.locked():
            RATE_LIMITER_REJECTIONS.labels(reason="inference_budget").inc()
            raise HTTPException(status_code=429, detail="Inference concurrency budget exhausted")
        await inference_budget.acquire()
        started = time.perf_counter()
        try:
            return await run_in_threadpool(model_service.predict, requests)
        finally:
            serving_mode = str(_service_diagnostics(model_service).get("serving_mode", "unknown"))
            INFERENCE_LATENCY.labels(
                "batch" if len(requests) > 1 else "single", serving_mode
            ).observe(time.perf_counter() - started)
            inference_budget.release()

    @application.post("/predict", response_model=PredictionResponse, tags=["prediction"])
    async def predict(request: PredictionRequest) -> PredictionResponse:
        try:
            return _enrich_prediction((await bounded_predict([request]))[0], request.content())
        except RuntimeError as exc:
            logger.error("prediction_unavailable", endpoint="single", status_code=503)
            raise HTTPException(status_code=503, detail="Prediction service unavailable") from exc
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail="Prediction request rejected") from exc

    @application.post("/predict/batch", response_model=BatchPredictionResponse, tags=["prediction"])
    async def predict_batch(request: BatchPredictionRequest) -> BatchPredictionResponse:
        try:
            predictions = [_enrich_prediction(prediction, request_item.content()) for prediction, request_item in zip(await bounded_predict(request.requests), request.requests, strict=True)]
        except RuntimeError as exc:
            logger.error("prediction_unavailable", endpoint="batch", status_code=503)
            raise HTTPException(status_code=503, detail="Prediction service unavailable") from exc
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail="Batch prediction request rejected") from exc
        model_name = predictions[0].model_name if predictions else "unknown"
        artifact_version = predictions[0].artifact_version if predictions else "unknown"
        return BatchPredictionResponse(predictions=predictions, count=len(predictions), model_name=model_name, artifact_version=artifact_version)

    return application


app = create_app()
