from __future__ import annotations

import asyncio
import base64
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from fastapi.testclient import TestClient
from scipy.sparse import csr_matrix

from src.features.minhash import find_near_duplicate_groups
from src.features.text import TfidfTextPipeline
from src.features.unsupervised_features import UnsupervisedFeatureAugmenter
from src.models.bert import validate_offline_bundle
from src.serving.app import PredictionResponse, RateLimiter, create_app
from src.serving.export import (
    _canonical_manifest_bytes,
    build_package_manifest,
    export_onnx_sklearn,
    onnx_predict_proba,
    sha256_file,
    verify_package_manifest,
)
from src.serving.rate_limiter import RedisRateLimiter


class ReadyService:
    ready = True
    error = None
    artifact_path = "fixture"

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


class BlockingService(ReadyService):
    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()

    def predict(self, requests: list[Any]) -> list[PredictionResponse]:
        self.started.set()
        if not self.release.wait(timeout=5):
            raise RuntimeError("blocking fixture timed out")
        return super().predict(requests)


def poll_drift(client: TestClient, response: Any) -> dict[str, Any]:
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    for _ in range(100):
        status_response = client.get(f"/monitoring/drift/{job_id}")
        assert status_response.status_code == 200
        payload = status_response.json()
        if payload["status"] in {"completed", "failed", "expired"}:
            return payload
    pytest.fail("Drift job did not reach a terminal state")


def test_inference_semaphore_returns_429_when_budget_is_exhausted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_INFLIGHT_INFERENCE", "1")
    service = BlockingService()
    with TestClient(create_app(service, RateLimiter(limit=100, window_seconds=60))) as client:
        with ThreadPoolExecutor(max_workers=1) as executor:
            first = executor.submit(client.post, "/predict", json={"text": "first"})
            assert service.started.wait(timeout=2)
            second = client.post("/predict", json={"text": "second"})
            assert second.status_code == 429
            service.release.set()
            assert first.result(timeout=5).status_code == 200


def test_async_drift_returns_job_id_and_completed_result() -> None:
    with TestClient(create_app(ReadyService(), RateLimiter(limit=100, window_seconds=60))) as client:
        response = client.post(
            "/monitoring/drift",
            json={
                "reference": {"feature_0": list(range(20))},
                "current": {"feature_0": list(range(10, 30))},
                "psi_threshold": 0.0,
            },
        )
        payload = poll_drift(client, response)
        assert payload["status"] == "completed"
        assert payload["result"]["drift_detected"] is True
        assert client.get("/monitoring/drift/not-found").status_code == 404


def test_signed_manifest_accepts_valid_signature_and_rejects_digest_mismatch(tmp_path: Path) -> None:
    ed25519 = pytest.importorskip("cryptography.hazmat.primitives.asymmetric.ed25519")
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    native_path = tmp_path / "model.joblib"
    native_path.write_bytes(b"signed-fixture")
    manifest = build_package_manifest("fixture", native_path, {"feature_schema": {}})
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key_b64 = base64.b64encode(private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()
    manifest["signature"] = {
        "algorithm": "Ed25519",
        "signature_b64": base64.b64encode(private_key.sign(_canonical_manifest_bytes(manifest))).decode(),
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    verified = verify_package_manifest(manifest_path, native_path, public_key_b64=public_key_b64)
    assert verified["native_artifact"]["sha256"] == sha256_file(native_path)
    manifest["native_artifact"]["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="digest"):
        verify_package_manifest(manifest_path, native_path, public_key_b64=public_key_b64)


def test_onnx_helpers_reject_sparse_tfidf_features(tmp_path: Path) -> None:
    pytest.importorskip("skl2onnx")
    pytest.importorskip("onnxruntime")
    sparse_features = csr_matrix(np.eye(2, dtype=np.float32))
    with pytest.raises(ValueError, match="sparse"):
        export_onnx_sklearn(object(), tmp_path / "model.onnx", sparse_features)
    with pytest.raises(ValueError, match="sparse"):
        onnx_predict_proba(tmp_path / "missing.onnx", sparse_features)


def test_air_gapped_bert_bundle_validation(tmp_path: Path) -> None:
    bundle = tmp_path / "bert-base-uncased"
    bundle.mkdir()
    (bundle / "config.json").write_text(json.dumps({"model_type": "bert"}), encoding="utf-8")
    (bundle / "vocab.txt").write_text("[UNK]\n", encoding="utf-8")
    (bundle / "model.safetensors").write_bytes(b"fixture")
    assert validate_offline_bundle(bundle) == bundle
    (bundle / "model.safetensors").unlink()
    with pytest.raises(FileNotFoundError, match="model.safetensors"):
        validate_offline_bundle(bundle)


def test_streaming_tfidf_fit_accepts_generator() -> None:
    texts = (text for text in ["real report alpha", "fake report beta", "real report gamma"])
    pipeline = TfidfTextPipeline(min_df=1, max_features=100)
    pipeline.fit(texts)
    matrix = pipeline.transform(["new report alpha"])
    assert matrix.shape[0] == 1
    assert matrix.shape[1] == len(pipeline.get_feature_names())


def test_streaming_minhash_detects_near_duplicates() -> None:
    base = "Title 0 Article text 0 with distinct token 0"
    groups = find_near_duplicate_groups(
        [base, base + " additional syndicated sentence", "unrelated article with different vocabulary"],
        threshold=0.5,
    )
    assert [0, 1] in groups


def test_online_unsupervised_features_reject_dbscan() -> None:
    with pytest.raises(ValueError, match="offline-only"):
        UnsupervisedFeatureAugmenter(online=True, include_dbscan=True).fit(np.zeros((4, 2)))


def test_redis_limiter_uses_atomic_eval_result(monkeypatch: pytest.MonkeyPatch) -> None:
    import redis.asyncio as redis_asyncio

    class FakeRedis:
        def __init__(self) -> None:
            self.results = [[1, 4500], [0, 1200]]
            self.calls: list[tuple[Any, ...]] = []

        async def eval(self, *args: Any) -> list[int]:
            self.calls.append(args)
            return self.results.pop(0)

        async def aclose(self) -> None:
            return None

    fake = FakeRedis()
    monkeypatch.setattr(redis_asyncio, "from_url", lambda *args, **kwargs: fake)
    limiter = RedisRateLimiter("redis://fixture", limit=1, window_seconds=60)
    assert asyncio.run(limiter.check_async("client")) == (True, 0)
    assert asyncio.run(limiter.check_async("client")) == (False, 2)
    assert len(fake.calls) == 2
    asyncio.run(limiter.close())
