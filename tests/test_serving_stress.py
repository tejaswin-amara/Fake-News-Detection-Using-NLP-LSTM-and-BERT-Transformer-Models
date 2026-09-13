from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import psutil
from fastapi.testclient import TestClient
from scipy.sparse import csr_matrix

from src.serving.app import PredictionResponse, RateLimiter, create_app


class HighDimensionalService:
    ready = True
    error: str | None = None

    def predict(self, requests: list[Any]) -> list[PredictionResponse]:
        rows = len(requests)
        vocabulary_width = 200_000
        row_indices = np.arange(rows, dtype=np.int32)
        column_indices = np.arange(rows, dtype=np.int32) % vocabulary_width
        values = np.ones(rows, dtype=np.float32)
        matrix = csr_matrix((values, (row_indices, column_indices)), shape=(rows, vocabulary_width), dtype=np.float32)
        assert matrix.shape == (rows, vocabulary_width)
        return [
            PredictionResponse(
                label=0,
                label_name="real",
                probability_real=0.75,
                probability_fake=0.25,
                model_name="stress-fixture",
                artifact_version="stress-v1",
            )
            for _ in requests
        ]


def test_max_batch_200k_feature_sparse_memory_budget() -> None:
    process = psutil.Process()
    before = process.memory_info().rss
    client = TestClient(create_app(HighDimensionalService(), RateLimiter(limit=100, window_seconds=60)))
    payload = {"requests": [{"text": f"article {index}"} for index in range(64)]}
    response = client.post("/predict/batch", json=payload)
    after = process.memory_info().rss
    delta = max(0, after - before)
    assert response.status_code == 200
    assert response.json()["count"] == 64
    assert delta < 700 * 1024 * 1024
    report = {
        "test": "max_batch_200k_feature_sparse_memory_budget",
        "batch_size": 64,
        "vocabulary_features": 200_000,
        "rss_before_bytes": before,
        "rss_after_bytes": after,
        "rss_delta_bytes": delta,
        "compose_memory_limit_bytes": 1_073_741_824,
        "within_configured_limit_with_margin": True,
    }
    output = Path("reports/serving_stress_memory.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
