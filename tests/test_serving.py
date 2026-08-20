from __future__ import annotations

from fastapi.testclient import TestClient

from src.serving.app import create_app


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
