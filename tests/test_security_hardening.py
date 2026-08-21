from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from fastapi.testclient import TestClient

from scripts.synthetic_traffic import TrafficConfig
from src.monitoring.drift import (
    build_retraining_signal,
    monitor_prediction_probabilities,
    population_stability_index,
)
from src.serving.app import PredictionResponse, RateLimiter, create_app
from src.serving.predictor import OnnxRuntimeConfig
from src.tracking import initialize_tracking


class HardenedFakeService:
    ready = True
    error: str | None = None

    def predict(self, requests: list[Any]) -> list[PredictionResponse]:
        return [
            PredictionResponse(
                label=0,
                label_name="real",
                probability_real=0.8,
                probability_fake=0.2,
                model_name="fixture",
                artifact_version="fixture-v1",
            )
            for _ in requests
        ]


def test_rate_limiter_returns_retry_after_and_evicts_old_clients() -> None:
    limiter = RateLimiter(limit=1, window_seconds=10.0, max_clients=2)
    assert limiter.check("a", now=0.0) == (True, 0)
    allowed, retry_after = limiter.check("a", now=1.0)
    assert allowed is False
    assert retry_after >= 1
    assert limiter.check("a", now=11.0) == (True, 0)
    assert limiter.check("b", now=12.0) == (True, 0)
    assert limiter.check("c", now=13.0) == (True, 0)


def test_api_rejects_unknown_fields_control_characters_and_massive_batches() -> None:
    client = TestClient(create_app(HardenedFakeService(), RateLimiter(limit=100, window_seconds=60)))
    assert client.post("/predict", json={"text": "clean", "unexpected": "field"}).status_code == 422
    assert client.post("/predict", json={"text": "bad\u0000payload"}).status_code == 422
    massive = {"requests": [{"text": "clean"}] * 65}
    assert client.post("/predict/batch", json=massive).status_code == 422


def test_api_rejects_oversized_http_body_before_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_REQUEST_BYTES", "32")
    client = TestClient(create_app(HardenedFakeService(), RateLimiter(limit=100, window_seconds=60)))
    response = client.post("/predict", content='{"text":"' + ("x" * 100) + '"}', headers={"content-type": "application/json"})
    assert response.status_code == 413


def test_api_rate_limit_and_cors_are_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://example.com")
    client = TestClient(create_app(HardenedFakeService(), RateLimiter(limit=1, window_seconds=60)))
    first = client.post("/predict", json={"text": "clean"}, headers={"Origin": "https://example.com"})
    second = client.post("/predict", json={"text": "clean"})
    assert first.status_code == 200
    assert first.headers["access-control-allow-origin"] == "https://example.com"
    assert second.status_code == 429
    assert "retry-after" in second.headers
    assert client.get("/health").status_code == 200


def test_cors_wildcard_credentials_configuration_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*")
    monkeypatch.setenv("CORS_ALLOW_CREDENTIALS", "true")
    with pytest.raises(ValueError, match="Wildcard CORS"):
        create_app(HardenedFakeService())


def test_drift_is_finite_for_equal_and_different_constant_distributions() -> None:
    assert population_stability_index([1.0, 1.0], [1.0, 1.0]) == 0.0
    changed = population_stability_index([1.0, 1.0], [2.0, 2.0])
    assert np.isfinite(changed)
    report = monitor_prediction_probabilities([0.0, 0.0], [1.0, 1.0], psi_threshold=0.0)
    assert np.isfinite(report["psi"])
    assert json.dumps(report, allow_nan=False)


def test_drift_rejects_non_finite_probabilities_and_invalid_signal() -> None:
    with pytest.raises(ValueError, match="finite"):
        monitor_prediction_probabilities([0.1, float("nan")], [0.2, 0.3])
    with pytest.raises(ValueError, match="sequence"):
        build_retraining_signal({"drifted_features": "bad"}, "v1", "w1")


def test_onnx_runtime_configuration_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        OnnxRuntimeConfig(providers=(), intra_op_num_threads=1, inter_op_num_threads=1)
    with pytest.raises(ValueError):
        OnnxRuntimeConfig(intra_op_num_threads=0)
    with pytest.raises(ValueError):
        OnnxRuntimeConfig(graph_optimization_level="invalid")


def test_tracking_fallback_is_used_after_primary_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[str] = []

    def fake_initialize(uri: str, experiment_name: str, artifact_location: str | None) -> dict[str, str]:
        del experiment_name, artifact_location
        calls.append(uri)
        if uri == "primary":
            raise ConnectionError("tracking server unavailable")
        return {"tracking_uri": uri, "experiment_name": "fixture", "experiment_id": "1", "artifact_location": uri}

    monkeypatch.setattr("src.tracking._initialize_tracking_once", fake_initialize)
    result = initialize_tracking(
        tracking_uri="primary",
        experiment_name="fixture",
        local_fallback_uri=str(tmp_path / "fallback"),
        retry_attempts=2,
        retry_backoff_seconds=0.0,
    )
    assert result["fallback_used"] == "true"
    assert calls == ["primary", "primary", str(tmp_path / "fallback")]


def test_synthetic_traffic_configuration_is_bounded() -> None:
    config = TrafficConfig("http://api", 0.0, 2, 1.0, 3)
    assert config.max_requests == 3


def test_model_artifact_requires_matching_sha256(tmp_path: Path) -> None:
    import hashlib

    import joblib

    from src.serving.export import load_native_artifact

    artifact_path = tmp_path / "artifact.joblib"
    joblib.dump({"model": "fixture"}, artifact_path)
    digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    assert load_native_artifact(artifact_path, digest)["model"] == "fixture"
    with pytest.raises(ValueError, match="digest mismatch"):
        load_native_artifact(artifact_path, "0" * 64)
    with pytest.raises(ValueError, match="required"):
        load_native_artifact(artifact_path)


def test_low_signal_flag_for_punctuation_payload() -> None:
    client = TestClient(create_app(HardenedFakeService(), RateLimiter(limit=100, window_seconds=60)))
    response = client.post("/predict", json={"text": "!!! ??? ..."})
    assert response.status_code == 200
    assert response.json()["low_signal"] is True


def test_benjamini_hochberg_metadata_is_present() -> None:
    client = TestClient(create_app(HardenedFakeService(), RateLimiter(limit=100, window_seconds=60)))
    response = client.post(
        "/monitoring/drift",
        json={"reference": {"a": [0.0, 0.0, 0.0], "b": [0.0, 0.0, 0.0]}, "current": {"a": [0.0, 0.0, 0.0], "b": [1.0, 1.0, 1.0]}},
    )
    assert response.status_code == 200
    assert response.json()["numeric"]["multiple_testing"]["method"] == "benjamini_hochberg"


def test_multi_worker_without_distributed_limiter_is_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEB_CONCURRENCY", "2")
    monkeypatch.delenv("DISTRIBUTED_RATE_LIMITER", raising=False)
    with pytest.raises(ValueError, match="DISTRIBUTED_RATE_LIMITER"):
        create_app(HardenedFakeService())
