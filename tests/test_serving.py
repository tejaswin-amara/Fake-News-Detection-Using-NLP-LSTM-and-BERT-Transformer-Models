from __future__ import annotations

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression

from src.monitoring.drift import monitor_features
from src.serving.app import create_app
from src.serving.export import export_onnx_sklearn


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


def test_validation_rejects_empty_text():
    client = TestClient(create_app(FakeService()))
    response = client.post("/predict", json={"title": "", "text": ""})
    assert response.status_code == 422


def test_drift_monitoring_hook_reports_ks_and_psi():
    client = TestClient(create_app(FakeService()))
    reference = {"feature_0": list(range(100))}
    current = {"feature_0": list(range(50, 150))}
    response = client.post(
        "/monitoring/drift",
        json={"reference": reference, "current": current, "psi_threshold": 0.0},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["drift_detected"] is True
    assert "ks" in payload["features"]["feature_0"]
    assert "psi" in payload["features"]["feature_0"]
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
