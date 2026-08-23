from __future__ import annotations

import json
import time

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression

from src.monitoring.drift import (
    build_retraining_signal,
    monitor_features,
    monitor_prediction_probabilities,
    monitor_text_batch,
)
from src.serving.app import create_app
from src.serving.export import assert_onnx_parity, export_onnx_sklearn, onnx_predict_proba


def poll_drift(client: TestClient, response) -> dict:
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    for _ in range(100):
        status_response = client.get(f"/monitoring/drift/{job_id}")
        assert status_response.status_code == 200
        payload = status_response.json()
        if payload["status"] in {"completed", "failed", "expired"}:
            return payload
        time.sleep(0.01)
    pytest.fail("Drift job did not reach a terminal state")


class FakeService:
    artifact_path = "fixture"
    error = None
    ready = True

    def predict(self, requests):
        from src.serving.app import PredictionResponse

        outputs = []
        for request in requests:
            probability_fake = 0.8 if "fake" in request.content().lower() else 0.2
            label = int(probability_fake >= 0.5)
            outputs.append(
                PredictionResponse(
                    label=label,
                    label_name="fake" if label else "real",
                    probability_real=1 - probability_fake,
                    probability_fake=probability_fake,
                    model_name="fixture",
                    artifact_version="fixture-v1",
                )
            )
        return outputs


def test_health_predict_batch_and_latency():
    client = TestClient(create_app(FakeService()))
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["model_ready"] is True
    response = client.post("/predict", json={"title": "", "text": "This is a fake claim"})
    assert response.status_code == 200
    assert response.json()["label"] == 1
    assert "X-Process-Time-Ms" in response.headers
    batch = client.post(
        "/predict/batch",
        json={"requests": [{"text": "real report"}, {"text": "fake report"}]},
    )
    assert batch.status_code == 200
    assert batch.json()["count"] == 2


def test_openapi_contract_headers_and_json_boundary_are_safe():
    client = TestClient(create_app(FakeService()))
    schema_response = client.get("/openapi.json")
    assert schema_response.status_code == 200
    schema = schema_response.json()
    assert schema["info"]["title"] == "Fake News Detection API"
    assert set(("/health", "/ready", "/predict", "/predict/batch", "/monitoring/drift")).issubset(schema["paths"])
    assert "/metrics" not in schema["paths"]
    assert "System startup warm-up article." not in json.dumps(schema)

    response = client.post("/predict", json={"text": "synthetic contract fixture"})
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Content-Security-Policy"] == "frame-ancestors 'none'"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"

    sentinel = "raw-article-content-must-not-appear-in-error"
    rejected = client.post("/predict", content=sentinel, headers={"Content-Type": "text/plain"})
    assert rejected.status_code == 415
    assert sentinel not in rejected.text
    assert rejected.json()["detail"] == "This endpoint requires application/json"


def test_health_and_readiness_never_expose_internal_diagnostics():
    class UnavailableService:
        ready = False
        error = "sensitive internal diagnostic /private/artifact.path"
        artifact_path = "/private/artifact.path"

        def predict(self, requests):
            raise RuntimeError("not available")

    with TestClient(create_app(UnavailableService())) as client:
        health = client.get("/health")
        ready = client.get("/ready")
    assert health.status_code == 200
    assert health.json()["status"] == "degraded"
    assert "sensitive internal diagnostic" not in health.text
    assert "/private/artifact.path" not in health.text
    assert ready.status_code == 503
    assert ready.json()["detail"] == "Serving readiness check failed"
    assert "sensitive internal diagnostic" not in ready.text


def test_validation_rejects_empty_text():
    client = TestClient(create_app(FakeService()))
    response = client.post("/predict", json={"title": "", "text": ""})
    assert response.status_code == 422


def test_drift_monitoring_hook_reports_ks_and_psi():
    with TestClient(create_app(FakeService())) as client:
        reference = {"feature_0": list(range(100))}
        current = {"feature_0": list(range(50, 150))}
        response = client.post(
            "/monitoring/drift",
            json={"reference": reference, "current": current, "psi_threshold": 0.0},
        )
        payload = poll_drift(client, response)
        assert payload["status"] == "completed"
        result = payload["result"]
        assert result["drift_detected"] is True
        assert "ks" in result["features"]["feature_0"]
        assert "psi" in result["features"]["feature_0"]
        assert client.post("/predict", json={"text": "fake report"}).status_code == 200
    direct = monitor_features(reference, current, psi_threshold=0.0)
    assert direct["drift_detected"] is True


def test_onnx_packaging_verification(tmp_path):
    pytest.importorskip("skl2onnx")
    ort = pytest.importorskip("onnxruntime")
    features = np.asarray([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]], dtype=np.float32)
    labels = np.asarray([0, 0, 1, 1])
    model = LogisticRegression(max_iter=1000).fit(features, labels)
    output = export_onnx_sklearn(model, tmp_path / "model.onnx", features)
    assert output.exists()
    session = ort.InferenceSession(str(output), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: features[:2]})
    assert outputs
    assert len(outputs[0]) == 2


def test_readiness_and_extended_response_schema():
    client = TestClient(create_app(FakeService()))
    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    response = client.post("/predict", json={"text": "fake report"})
    payload = response.json()
    assert payload["raw_probability_fake"] == payload["probability_fake"]
    assert payload["calibrated_probability_fake"] == payload["probability_fake"]
    assert payload["confidence_interval_low"] is None
    assert payload["confidence_interval_high"] is None
    assert payload["calibration_status"] == "not_available"


def test_serving_rejects_whitespace_and_malformed_batch():
    client = TestClient(create_app(FakeService()))
    assert client.post("/predict", json={"text": "   "}).status_code == 422
    assert client.post("/predict/batch", json={"requests": []}).status_code == 422
    assert client.post("/predict/batch", json={"requests": [{"text": " "}]}).status_code == 422
    assert client.post("/predict", json={"text": "x" * 50_001}).status_code == 422


def test_probability_text_drift_and_retraining_signal():
    probability = monitor_prediction_probabilities([0.1] * 50 + [0.9] * 50, [0.99] * 100, psi_threshold=0.01)
    assert probability["drift_detected"] is True
    text = monitor_text_batch(
        ["short real report" for _ in range(20)],
        ["very long unseen phrase " * 10 for _ in range(20)],
        oov_threshold=0.01,
        length_threshold=0.01,
    )
    assert text["drift_detected"] is True
    signal = build_retraining_signal({"drift_detected": True, "drifted_features": ["oov_rate"]}, "baseline-v1", "window-1")
    assert signal["triggered"] is True
    assert signal["requires_human_approval"] is True
    assert signal["side_effects"] == "none"


def test_onnx_runtime_parity_is_below_tolerance(tmp_path):
    pytest.importorskip("skl2onnx")
    pytest.importorskip("onnxruntime")
    features = np.asarray([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]], dtype=np.float32)
    labels = np.asarray([0, 0, 1, 1])
    model = LogisticRegression(max_iter=1000).fit(features, labels)
    output = export_onnx_sklearn(model, tmp_path / "model.onnx", features)
    onnx_probabilities = onnx_predict_proba(output, features)
    report = assert_onnx_parity(model.predict_proba(features), onnx_probabilities, epsilon=1e-5)
    assert report["passed"] is True
    assert report["max_absolute_error"] < 1e-5


def test_readiness_fails_when_artifact_is_missing(tmp_path):
    from src.serving.app import ModelService

    client = TestClient(create_app(ModelService(tmp_path / "missing.joblib")))
    assert client.get("/health").json()["status"] == "degraded"
    assert client.get("/ready").status_code == 503


def test_drift_endpoint_accepts_probability_and_text_payloads():
    with TestClient(create_app(FakeService())) as client:
        probability_response = client.post(
            "/monitoring/drift",
            json={
                "reference_probabilities": [0.1] * 20,
                "current_probabilities": [0.9] * 20,
                "psi_threshold": 0.01,
                "baseline_revision": "fixture-v1",
                "window_id": "window-1",
            },
        )
        probability_payload = poll_drift(client, probability_response)
        assert probability_payload["status"] == "completed"
        assert probability_payload["result"]["probability"]["drift_detected"] is True
        text_response = client.post(
            "/monitoring/drift",
            json={
                "reference_texts": ["short known report"] * 20,
                "current_texts": ["unseen phrase " * 10] * 20,
                "oov_threshold": 0.01,
                "length_threshold": 0.01,
            },
        )
        text_payload = poll_drift(client, text_response)
        assert text_payload["status"] == "completed"
        assert text_payload["result"]["text"]["drift_detected"] is True
