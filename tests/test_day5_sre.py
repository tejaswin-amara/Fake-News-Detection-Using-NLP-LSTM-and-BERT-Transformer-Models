from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from fastapi.testclient import TestClient
from scipy.sparse import csr_matrix

import src.serving.app as app_module
from src.config import ProjectConfig, ensure_directories, load_config
from src.features.minhash import (
    StreamingMinHashLSH,
    find_near_duplicate_groups,
    minhash_signature,
    shingles,
)
from src.features.text import (
    TextNormalizer,
    TextStatisticsTransformer,
    TfidfTextPipeline,
    clean_text,
    process_tokens,
    tokenize_text,
)
from src.monitoring.drift import (
    build_retraining_signal,
    ks_drift,
    monitor_features,
    monitor_prediction_probabilities,
    monitor_text_batch,
    population_stability_index,
    save_report,
)
from src.monitoring.jobs import DriftJobManager
from src.serving.app import (
    DriftRequest,
    ModelService,
    PredictionRequest,
    PredictionResponse,
    _client_key,
    _enrich_prediction,
    _env_bool,
    _env_csv,
    _env_float,
    _env_int,
    _process_drift_payload,
    _service_diagnostics,
    _validate_text_value,
)
from src.serving.export import (
    artifact_metadata,
    assert_onnx_parity,
    build_package_manifest,
    export_onnx_sklearn,
    load_native_artifact,
    load_verified_native_artifact,
    onnx_parity_report,
    onnx_predict_proba,
    save_native_artifact,
    verify_package_manifest,
    write_export_metadata,
)
from src.serving.predictor import (
    OnnxRuntimeConfig,
    OnnxTextModel,
    PackagedTextModel,
    _validate_probability_matrix,
    warmup_text_model,
)
from src.serving.rate_limiter import RedisRateLimiter


class DummyPipeline:
    def transform(self, values: list[str]) -> np.ndarray[Any, Any]:
        return np.asarray([[len(value), 1.0] for value in values], dtype=np.float32)


class DummyFeatureTransformer:
    def transform(self, values: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        return values + 1


class DummyEstimator:
    def predict_proba(self, features: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        del features
        return np.asarray([[0.7, 0.3]], dtype=np.float64)

    def predict(self, features: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        return np.zeros(len(features), dtype=np.int64)


class DummyInput:
    name = "features"


class DummySession:
    def __init__(self, outputs: list[Any] | None = None) -> None:
        self.outputs = outputs or [np.asarray([0]), np.asarray([[0.7, 0.3]], dtype=np.float32)]

    def get_inputs(self) -> list[DummyInput]:
        return [DummyInput()]

    def run(self, output_names: Any, feed: dict[str, Any]) -> list[Any]:
        del output_names, feed
        return self.outputs


class WarmupModel:
    def __init__(self, values: np.ndarray[Any, Any]) -> None:
        self.values = values
        self.calls = 0

    def predict_proba(self, texts: list[str]) -> np.ndarray[Any, Any]:
        self.calls += len(texts)
        return self.values


def test_config_helpers_and_directory_creation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("project:\n  random_seed: 17\npaths:\n  reports: reports\n", encoding="utf-8")
    config = load_config(config_path, root=tmp_path)
    assert config.seed == 17
    assert config.paths["reports"] == tmp_path / "reports"
    ensure_directories(config)
    assert (tmp_path / "reports").is_dir()

    monkeypatch.setenv("TEST_BOOL", "yes")
    monkeypatch.setenv("TEST_INT", "4")
    monkeypatch.setenv("TEST_FLOAT", "1.5")
    monkeypatch.setenv("TEST_CSV", "a, b,,c")
    assert _env_bool("TEST_BOOL", False) is True
    assert _env_int("TEST_INT", 0) == 4
    assert _env_float("TEST_FLOAT", 0.0) == 1.5
    assert _env_csv("TEST_CSV") == ("a", "b", "c")
    assert _env_bool("MISSING_BOOL", True) is True
    assert _env_csv("MISSING_CSV", ("default",)) == ("default",)


def test_project_config_defaults_and_invalid_requests() -> None:
    config = ProjectConfig(root=Path("."), values={})
    assert config.seed == 42
    assert config.paths == {}
    with pytest.raises(ValueError):
        PredictionRequest(text="")
    with pytest.raises(ValueError):
        PredictionRequest(title="\x00", text="valid")
    with pytest.raises(ValueError):
        DriftRequest(reference={"x": [1.0]}, current={"x": [2.0]})
    with pytest.raises(ValueError):
        DriftRequest(reference={"x": [1.0, 2.0]}, current=None)


def test_packaged_predictor_and_warmup_contracts() -> None:
    model = PackagedTextModel(DummyPipeline(), DummyEstimator(), DummyFeatureTransformer())
    probabilities = model.predict_proba(["article"])
    assert probabilities.shape == (1, 2)
    assert model.predict(["article"]).tolist() == [0]
    warmup_model = WarmupModel(np.asarray([[0.8, 0.2]], dtype=np.float64))
    warmup_text_model(warmup_model)
    assert warmup_model.calls == 1


def test_onnx_predictor_dense_and_probability_validation() -> None:
    model = OnnxTextModel(DummyPipeline(), DummySession())
    assert model.predict_proba(["article"]).shape == (1, 2)
    list_output_model = OnnxTextModel(
        DummyPipeline(), DummySession([np.asarray([0]), [{0: 0.6, 1: 0.4}]])
    )
    assert np.allclose(list_output_model.predict_proba(["article"]), [[0.6, 0.4]])
    sparse_pipeline = type("SparsePipeline", (), {"transform": lambda self, values: csr_matrix([[1.0, 2.0]])})()
    with pytest.raises(RuntimeError, match="sparse"):
        OnnxTextModel(sparse_pipeline, DummySession()).predict_proba(["article"])
    with pytest.raises(ValueError, match="no input"):
        OnnxTextModel(type("Pipeline", (), {})(), type("Session", (), {"get_inputs": lambda self: []})())


def test_predictor_configuration_and_probability_errors() -> None:
    with pytest.raises(ValueError):
        OnnxRuntimeConfig(providers=())
    with pytest.raises(ValueError):
        OnnxRuntimeConfig(intra_op_num_threads=0)
    with pytest.raises(ValueError):
        OnnxRuntimeConfig(graph_optimization_level="invalid")
    for values in (
        np.asarray([[0.2]]),
        np.asarray([[np.nan, 0.5]]),
        np.asarray([[-0.1, 1.1]]),
        np.asarray([[0.2, 0.2]]),
    ):
        with pytest.raises(RuntimeError):
            _validate_probability_matrix(values, 1)


def test_redis_breaker_open_path_is_nonblocking() -> None:
    async def exercise() -> tuple[bool, int]:
        limiter = RedisRateLimiter("redis://fixture", failure_threshold=1, recovery_timeout_seconds=60)
        limiter._state = "open"
        limiter._opened_at = asyncio.get_running_loop().time()
        return await limiter.check_async("client")

    assert asyncio.run(exercise()) == (True, 0)


def test_model_service_diagnostics_prediction_and_close(tmp_path: Path) -> None:
    service = ModelService(tmp_path / "missing.joblib")
    service.load()
    assert service.ready is False
    assert service.diagnostics()["model_ready"] is False
    service.model = PackagedTextModel(DummyPipeline(), DummyEstimator())
    service.metadata = {
        "model_name": "fixture",
        "artifact_version": "v1",
        "calibration_status": "calibrated",
        "confidence_interval": {"low": 0.1, "high": 0.9},
    }
    predictions = service.predict([PredictionRequest(title="title", text="article")])
    assert predictions[0].label_name == "real"
    assert predictions[0].confidence_interval_low == 0.1
    assert predictions[0].confidence_interval_high == 0.9
    service.close()
    assert service.ready is False


def test_model_service_prediction_sparse_low_signal_and_errors() -> None:
    service = ModelService("fixture.joblib")
    service.model = PackagedTextModel(DummyPipeline(), DummyEstimator())
    with pytest.raises(RuntimeError, match="invalid probability"):
        service.model = type("BadModel", (), {"predict_proba": lambda self, texts: np.asarray([[0.5]])})()
        service.predict([PredictionRequest(text="article")])
    service.model = PackagedTextModel(DummyPipeline(), DummyEstimator())
    service.metadata = {}
    assert service.predict([PredictionRequest(text="article")])[0].low_signal is False
    assert _enrich_prediction(
        PredictionResponse(
            label=0,
            label_name="real",
            probability_real=1.0,
            probability_fake=0.0,
            model_name="fixture",
            artifact_version="v1",
        ),
        "!!!",
    ).low_signal is True


def test_app_helpers_and_drift_processing_branches() -> None:
    scope = {"type": "http", "client": ("10.0.0.1", 1234), "headers": [(b"x-forwarded-for", b"203.0.113.5, 10.0.0.1")]}
    from starlette.requests import Request

    request = Request(scope)
    assert _client_key(request, {"10.0.0.1"}) == "203.0.113.5"
    assert _client_key(request, set()) == "10.0.0.1"
    assert _service_diagnostics(type("Service", (), {"ready": True, "error": None})())["model_ready"] is True
    assert _enrich_prediction(
        PredictionResponse(
            label=1,
            label_name="fake",
            probability_real=0.2,
            probability_fake=0.8,
            model_name="fixture",
            artifact_version="v1",
        )
    ).raw_probability_fake == 0.8
    numeric = _process_drift_payload({"reference": {"x": [1.0, 2.0]}, "current": {"x": [2.0, 3.0]}})
    probability = _process_drift_payload({"reference_probabilities": [0.1, 0.2], "current_probabilities": [0.8, 0.9]})
    text = _process_drift_payload({"reference_texts": ["a b", "a b"], "current_texts": ["z z", "z z"]})
    assert "numeric" in numeric and "probability" in probability and "text" in text


def test_drift_request_all_validated_input_families() -> None:
    assert DriftRequest(reference={"x": [1.0, 2.0]}, current={"x": [2.0, 3.0]}).reference is not None
    assert DriftRequest(reference_probabilities=[0.1, 0.2], current_probabilities=[0.8, 0.9]).reference_probabilities is not None
    assert DriftRequest(reference_texts=["a", "b"], current_texts=["c", "d"]).reference_texts is not None
    with pytest.raises(ValueError):
        DriftRequest(reference={"x": [float("nan"), 1.0]}, current={"x": [1.0, 2.0]})
    with pytest.raises(ValueError):
        DriftRequest(reference_probabilities=[0.1, 1.2], current_probabilities=[0.2, 0.3])
    with pytest.raises(ValueError):
        DriftRequest(reference_texts=["only"], current_texts=["two"])


def test_export_metadata_manifest_and_parity_helpers(tmp_path: Path) -> None:
    artifact_path = save_native_artifact({"fixture": True}, tmp_path / "model.joblib", {"model_name": "fixture"})
    artifact = load_native_artifact(artifact_path, expected_sha256=__import__("hashlib").sha256(artifact_path.read_bytes()).hexdigest())
    assert artifact["model"]["fixture"] is True
    metadata = artifact_metadata("fixture", {"label_mapping": {"real": 0, "fake": 1}})
    manifest = build_package_manifest("fixture", artifact_path, metadata)
    assert manifest["native_artifact"]["sha256"]
    metadata_path = write_export_metadata(metadata, tmp_path / "metadata.json")
    assert metadata_path.read_text(encoding="utf-8").startswith("{")
    report = onnx_parity_report([[0.2, 0.8]], [[0.2, 0.8]])
    assert report["passed"] is True
    assert assert_onnx_parity([[0.2, 0.8]], [[0.2, 0.8]])["passed"] is True
    with pytest.raises(AssertionError):
        assert_onnx_parity([[0.2, 0.8]], [[0.3, 0.7]])
    assert onnx_parity_report([[0.2, 0.8]], [[0.2]])["shape_match"] is False


def test_monitoring_statistics_and_retraining_signal() -> None:
    numeric = monitor_features({"x": [1.0, 1.0, 1.0]}, {"x": [2.0, 2.0, 2.0]})
    probabilities = monitor_prediction_probabilities([0.1, 0.1, 0.1], [0.9, 0.9, 0.9])
    texts = monitor_text_batch(["common words", "common words"], ["rare term", "rare term"])
    signal = build_retraining_signal({"drift_detected": True, "drifted_features": ["x"]}, baseline_revision="b", window_id="w")
    assert "features" in numeric
    assert "drift_detected" in probabilities
    assert "drift_detected" in texts
    assert signal["requires_human_approval"] is True


def test_drift_job_manager_lifecycle_and_failure() -> None:
    async def exercise() -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
        failures: list[str] = []

        def processor(payload: dict[str, Any]) -> dict[str, Any]:
            if payload.get("fail"):
                raise ValueError("fixture failure")
            return {"value": payload["value"]}

        manager = DriftJobManager(processor, maxsize=2, workers=1, ttl_seconds=1, on_failure=lambda exc: failures.append(type(exc).__name__))
        await manager.start()
        success_id = await manager.submit({"value": 3})
        failure_id = await manager.submit({"fail": True})
        await manager.queue.join()
        success = manager.status(success_id)
        failure = manager.status(failure_id)
        assert success is not None and success["status"] == "completed"
        assert failure is not None and failure["status"] == "failed"
        await manager.stop()
        stopped_error: dict[str, Any] | None = None
        try:
            await manager.submit({"value": 4})
        except RuntimeError as exc:
            stopped_error = {"error": type(exc).__name__}
        assert stopped_error == {"error": "RuntimeError"}
        return success, failure, failures

    success, failure, failures = asyncio.run(exercise())
    assert success is not None and failure is not None
    assert failures == ["ValueError"]


def test_text_processing_statistics_and_streaming_pipeline() -> None:
    assert clean_text(None) == ""
    assert clean_text(float("nan")) == ""
    cleaned = clean_text("<b>URL " + "https://" + "example.com</b> Email a@b.com", lowercase=False)
    assert "https://" not in cleaned and "a@b.com" not in cleaned
    assert tokenize_text("Hello, world!") == ["hello", "world"]
    assert process_tokens("The cats running", stop_words=None, stemming=True)
    assert process_tokens("The cats running", stop_words=["cats"], lemmatization=True)

    normalizer = TextNormalizer(stop_words=None, stemming=True).fit(["Cats running"])
    assert normalizer.transform(["Cats running"]).shape == (1,)
    with pytest.raises(RuntimeError):
        TextNormalizer().transform(["not fitted"])
    statistics = TextStatisticsTransformer().fit(["A sentence."])
    frame = statistics.transform(["A sentence with 123 words.", ""])
    assert list(frame.columns) == list(TextStatisticsTransformer.feature_names)
    assert statistics.get_feature_names_out().shape[0] == 9
    with pytest.raises(RuntimeError):
        TextStatisticsTransformer().transform(["not fitted"])

    pipeline = TfidfTextPipeline(min_df=1, max_df=1.0, stop_words=None)
    matrix = pipeline.fit_transform(text for text in ["alpha beta", "beta gamma"])
    assert matrix.shape[0] == 2
    assert pipeline.transform(text for text in ["alpha"]).shape[0] == 1
    assert pipeline.get_feature_names().size > 0
    assert pipeline.as_sklearn_pipeline().named_steps["tfidf"] is pipeline.vectorizer
    with pytest.raises(RuntimeError):
        TfidfTextPipeline(min_df=1).transform(["not fitted"])
    with pytest.raises(RuntimeError):
        TfidfTextPipeline(min_df=1).get_feature_names()


class SimpleService:
    ready = True
    error: str | None = None

    def __init__(self) -> None:
        self.closed = False

    def predict(self, requests: list[PredictionRequest]) -> list[PredictionResponse]:
        return [
            PredictionResponse(
                label=0,
                label_name="real",
                probability_real=0.8,
                probability_fake=0.2,
                model_name="simple",
                artifact_version="fixture",
            )
            for _ in requests
        ]

    def close(self) -> None:
        self.closed = True


def test_model_service_signed_load_and_runtime_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    artifact_path = tmp_path / "model.joblib"
    artifact_path.write_bytes(b"fixture")
    packaged = PackagedTextModel(DummyPipeline(), DummyEstimator())
    monkeypatch.setenv("PACKAGE_MANIFEST", str(tmp_path / "manifest.json"))
    monkeypatch.setenv("ARTIFACT_PUBLIC_KEY_B64", "public-key")
    monkeypatch.setattr(
        app_module,
        "load_verified_native_artifact",
        lambda *args, **kwargs: {"model": packaged, "metadata": {"model_name": "loaded"}},
    )
    service = ModelService(artifact_path)
    service.load()
    assert service.ready is True
    assert service.metadata["model_name"] == "loaded"
    service.load()
    service.close()
    assert service.ready is False


def test_create_app_configuration_guards(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*")
    monkeypatch.setenv("CORS_ALLOW_CREDENTIALS", "true")
    with pytest.raises(ValueError, match="Wildcard CORS"):
        app_module.create_app(SimpleService(), app_module.RateLimiter())
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS")
    monkeypatch.delenv("CORS_ALLOW_CREDENTIALS")
    monkeypatch.setenv("WEB_CONCURRENCY", "2")
    monkeypatch.delenv("DISTRIBUTED_RATE_LIMITER", raising=False)
    with pytest.raises(ValueError, match="WEB_CONCURRENCY"):
        app_module.create_app(SimpleService(), app_module.RateLimiter())
    monkeypatch.setenv("DISTRIBUTED_RATE_LIMITER", "redis")
    monkeypatch.setenv("MAX_INFLIGHT_INFERENCE", "0")
    with pytest.raises(ValueError, match="MAX_INFLIGHT"):
        app_module.create_app(SimpleService(), app_module.RateLimiter())
    monkeypatch.setenv("MAX_INFLIGHT_INFERENCE", "1")
    monkeypatch.setenv("MAX_REQUEST_BYTES", "0")
    with pytest.raises(ValueError, match="MAX_REQUEST_BYTES"):
        app_module.create_app(SimpleService(), app_module.RateLimiter())


def test_minhash_validation_and_grouping() -> None:
    assert shingles("", 5) == set()
    assert shingles("one two", 5) == {"one two"}
    with pytest.raises(ValueError):
        shingles("text", 0)
    with pytest.raises(ValueError):
        minhash_signature([], 3)
    assert len(minhash_signature([], 4)) == 4
    with pytest.raises(ValueError):
        StreamingMinHashLSH(threshold=0.0)
    with pytest.raises(ValueError):
        StreamingMinHashLSH(permutations=5, bands=2)
    with pytest.raises(ValueError):
        StreamingMinHashLSH(max_bucket_size=1)
    detector = StreamingMinHashLSH(permutations=4, bands=1, shingle_size=2)
    assert detector.rows_per_band == 4
    assert find_near_duplicate_groups(["same words here", "same words here", "different text"], permutations=4, bands=1, shingle_size=2)


def test_redis_limiter_validation_recovery_probe_and_close_failure() -> None:
    with pytest.raises(ValueError):
        RedisRateLimiter("redis://fixture", failure_threshold=0)

    async def exercise() -> None:
        limiter = RedisRateLimiter("redis://fixture", recovery_timeout_seconds=0.01)
        limiter._state = "open"
        limiter._opened_at = 0.0
        limiter._half_open_probe = True
        assert await limiter._probe_allowed() is False
        limiter._state = "half_open"
        limiter._half_open_probe = True
        assert await limiter._probe_allowed() is False

        class BrokenRedis:
            async def aclose(self) -> None:
                raise RuntimeError("close fixture")

        limiter._redis = BrokenRedis()
        await limiter.close()

    asyncio.run(exercise())


def test_onnx_runtime_from_artifact_and_missing_outputs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import sys
    import types

    class FakeGraph:
        ORT_DISABLE_ALL = "disable"
        ORT_ENABLE_BASIC = "basic"
        ORT_ENABLE_EXTENDED = "extended"
        ORT_ENABLE_ALL = "all"

    class FakeOptions:
        intra_op_num_threads = 0
        inter_op_num_threads = 0
        enable_cpu_mem_arena = False
        graph_optimization_level = None

    fake_ort = types.SimpleNamespace(
        SessionOptions=FakeOptions,
        GraphOptimizationLevel=FakeGraph,
        InferenceSession=lambda *args, **kwargs: DummySession(),
    )
    monkeypatch.setitem(sys.modules, "onnxruntime", fake_ort)
    packaged = types.SimpleNamespace(text_pipeline=DummyPipeline())
    model = OnnxTextModel.from_artifact(packaged, tmp_path / "fixture.onnx")
    assert model.input_name == "features"

    with pytest.raises(RuntimeError, match="outputs"):
        OnnxTextModel(DummyPipeline(), DummySession([np.asarray([0])])).predict_proba(["article"])


def test_drift_validation_edges_and_report_persistence(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        ks_drift([1.0, 2.0], [1.0, 2.0], alpha=0.0)
    with pytest.raises(ValueError):
        ks_drift([float("nan")], [1.0])
    with pytest.raises(ValueError):
        population_stability_index([1.0, 2.0], [1.0, 2.0], epsilon=0.0)
    assert population_stability_index([1.0, 1.0], [1.0, 1.0]) == 0.0
    with pytest.raises(ValueError):
        monitor_features({"x": [1.0, 2.0]}, {"y": [1.0, 2.0]})
    with pytest.raises(ValueError):
        monitor_features({"x": [1.0, 2.0]}, {"x": [1.0, 2.0]}, psi_threshold=-1.0)
    with pytest.raises(ValueError):
        monitor_prediction_probabilities([0.1, 2.0], [0.2, 0.3])
    with pytest.raises(ValueError):
        monitor_text_batch(["one"], ["two"])
    with pytest.raises(ValueError):
        monitor_text_batch(["a" * 50_001, "b"], ["c", "d"])
    with pytest.raises(ValueError):
        build_retraining_signal({}, "base", "window", cooldown_hours=-1)
    with pytest.raises(ValueError):
        build_retraining_signal({"drifted_features": "x"}, "base", "window")
    report_path = tmp_path / "reports" / "drift.json"
    save_report({"drift_detected": False}, report_path)
    assert report_path.exists()


def test_manifest_verification_and_sparse_onnx_rejections(tmp_path: Path) -> None:
    native_path = save_native_artifact({"model": "fixture"}, tmp_path / "native.joblib", {})
    manifest = build_package_manifest("fixture", native_path, {})
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    verified = verify_package_manifest(manifest_path, native_path, public_key_b64="", require_signature=False)
    assert verified["model_name"] == "fixture"
    bad_manifest = dict(manifest)
    bad_manifest["native_artifact"] = {"sha256": "0" * 64}
    manifest_path.write_text(json.dumps(bad_manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="digest"):
        verify_package_manifest(manifest_path, native_path, public_key_b64="", require_signature=False)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="Signed"):
        verify_package_manifest(manifest_path, native_path, public_key_b64="", require_signature=True)

    pytest.importorskip("skl2onnx")
    with pytest.raises(ValueError, match="sparse"):
        export_onnx_sklearn(object(), tmp_path / "model.onnx", csr_matrix([[1.0, 2.0]]))
    pytest.importorskip("onnxruntime")
    with pytest.raises(ValueError, match="sparse"):
        onnx_predict_proba(tmp_path / "missing.onnx", csr_matrix([[1.0, 2.0]]))


def test_create_app_redis_selection_and_warmup_degraded_path(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeRedisLimiter:
        def __init__(self, *args: Any) -> None:
            self.args = args

        async def check_async(self, client_key: str) -> tuple[bool, int]:
            del client_key
            return True, 0

        async def close(self) -> None:
            return None

    monkeypatch.setenv("DISTRIBUTED_RATE_LIMITER", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://fixture")
    monkeypatch.setattr(app_module, "RedisRateLimiter", FakeRedisLimiter)
    application = app_module.create_app(SimpleService())
    assert application is not None

    class NotReadyService(SimpleService):
        ready = False
        error: str | None = None

        def load(self) -> None:
            return None

    with TestClient(app_module.create_app(NotReadyService(), app_module.RateLimiter())) as client:
        assert client.get("/ready").status_code == 503


def test_async_shutdown_and_warmup_count_error_paths() -> None:
    class AsyncCloseService:
        ready = True
        error: str | None = None

        def predict(self, requests: list[PredictionRequest]) -> list[PredictionResponse]:
            return SimpleService().predict(requests)

        async def close(self) -> None:
            return None

    class EmptyWarmupService(SimpleService):
        def predict(self, requests: list[PredictionRequest]) -> list[PredictionResponse]:
            del requests
            return []

    class AsyncLimiter:
        async def check_async(self, client_key: str) -> tuple[bool, int]:
            del client_key
            return True, 0

        async def close(self) -> None:
            return None

    with TestClient(app_module.create_app(AsyncCloseService(), AsyncLimiter())) as client:
        assert client.get("/health").status_code == 200
    with TestClient(app_module.create_app(EmptyWarmupService(), AsyncLimiter())) as client:
        assert client.get("/ready").status_code == 503


def test_job_manager_queue_full_expiration_and_missing_job() -> None:
    async def exercise() -> None:
        with pytest.raises(ValueError):
            DriftJobManager(lambda payload: payload, maxsize=0)
        manager = DriftJobManager(lambda payload: payload, maxsize=1, workers=1, ttl_seconds=1)
        first = await manager.submit({"value": 1})
        with pytest.raises(OverflowError):
            await manager.submit({"value": 2})
        manager.jobs[first].created_at = 0.0
        assert manager.status(first)["status"] == "expired"  # type: ignore[index]
        assert manager.status("missing") is None
        await manager.start()
        manager.jobs.pop(first, None)
        manager.queue.get_nowait()
        manager.queue.task_done()
        manager.queue.put_nowait((first, {"value": 1}))
        await manager.queue.join()
        await manager.stop()

    asyncio.run(exercise())


def test_export_integrity_error_paths(tmp_path: Path) -> None:
    native_path = save_native_artifact({"model": "fixture"}, tmp_path / "native.joblib", {})
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        verify_package_manifest(manifest_path, native_path, public_key_b64="", require_signature=False)
    manifest = build_package_manifest("fixture", native_path, {})
    manifest["signature"] = {"signature_b64": "not-base64"}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="signature"):
        verify_package_manifest(manifest_path, native_path, public_key_b64="bad", require_signature=False)
    manifest["signature"] = {"signature_b64": "AA=="}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="public key"):
        verify_package_manifest(manifest_path, native_path, public_key_b64="", require_signature=False)
    with pytest.raises(ValueError, match="64-character"):
        load_native_artifact(native_path, expected_sha256="bad")
    import joblib

    malformed = tmp_path / "malformed.joblib"
    joblib.dump({"not_model": True}, malformed)
    with pytest.raises(ValueError, match="model"):
        load_native_artifact(malformed, expected_sha256=__import__("hashlib").sha256(malformed.read_bytes()).hexdigest())


def test_final_validation_and_artifact_helper_paths(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        _validate_text_value(123, "text", 10)
    with pytest.raises(ValueError):
        _validate_text_value("x" * 11, "text", 10)
    with pytest.raises(ValueError):
        DriftRequest(reference_probabilities=[0.1], current_probabilities=[0.2])
    with pytest.raises(ValueError):
        DriftRequest(reference={"x": [1.0, 2.0]}, current=None)
    with pytest.raises(ValueError):
        app_module.RateLimiter(limit=0)
    assert ModelService("fixture.joblib")._runtime_config().intra_op_num_threads >= 1

    native_path = save_native_artifact({"model": "fixture"}, tmp_path / "native.joblib", {})
    manifest = build_package_manifest("fixture", native_path, {})
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert load_verified_native_artifact(
        native_path,
        manifest_path,
        public_key_b64="",
        require_signature=False,
    )["model"]["model"] == "fixture"
    pytest.importorskip("skl2onnx")
    with pytest.raises(ValueError, match="two-dimensional"):
        export_onnx_sklearn(object(), tmp_path / "bad.onnx", np.asarray([1.0, 2.0]))


def test_onnx_probability_vector_is_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys
    import types

    fake_ort = types.SimpleNamespace(
        InferenceSession=lambda *args, **kwargs: DummySession(
            [np.asarray([0]), np.asarray([0.75], dtype=np.float32)]
        )
    )
    monkeypatch.setitem(sys.modules, "onnxruntime", fake_ort)
    probabilities = onnx_predict_proba("fixture.onnx", np.asarray([[1.0, 2.0]], dtype=np.float32))
    assert np.allclose(probabilities, [[0.25, 0.75]])


def test_final_app_rejection_and_drift_pair_branches() -> None:
    malformed = DriftRequest.model_construct(reference={"x": [1.0, 2.0]}, current=None)
    with pytest.raises(ValueError, match="complete"):
        malformed.validate_complete_pair()
    with TestClient(app_module.create_app(SimpleService(), app_module.RateLimiter())) as client:
        oversized = client.post(
            "/predict",
            headers={"content-length": "1000001"},
            content=b"{}",
        )
        assert oversized.status_code == 413
        invalid = client.post("/predict", json={"unexpected": "field"})
        assert invalid.status_code == 422


def test_model_service_lifespan_warmup_path() -> None:
    class PreloadedModelService(ModelService):
        def load(self) -> None:
            return None

    service = PreloadedModelService("fixture.joblib")
    service.model = WarmupModel(np.asarray([[0.8, 0.2]], dtype=np.float64))
    with TestClient(app_module.create_app(service, app_module.RateLimiter())) as client:
        assert client.get("/ready").status_code == 200


def test_drift_complete_pair_mismatch_branch() -> None:
    malformed = DriftRequest.model_construct(
        reference={"x": [1.0, 2.0]},
        current=None,
        reference_probabilities=[0.1, 0.2],
        current_probabilities=[0.8, 0.9],
    )
    with pytest.raises(ValueError, match="provided together"):
        malformed.validate_complete_pair()


def test_drift_vector_size_guard() -> None:
    with pytest.raises(ValueError, match="maximum"):
        ks_drift([1.0] * 10_001, [1.0, 2.0])
