from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import structlog
import yaml
from fastapi.testclient import TestClient

from src.config import configure_logging
from src.serving.app import PredictionResponse, RateLimiter, create_app
from src.serving.rate_limiter import RedisRateLimiter

ROOT = Path(__file__).resolve().parents[1]


class CountingService:
    ready = True
    error: str | None = None
    artifact_path = "fixture"

    def __init__(self) -> None:
        self.predict_calls = 0

    def predict(self, requests: list[Any]) -> list[PredictionResponse]:
        self.predict_calls += 1
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


class WarmupFailureService(CountingService):
    def predict(self, requests: list[Any]) -> list[PredictionResponse]:
        del requests
        self.predict_calls += 1
        raise RuntimeError("fixture warm-up failure")


def _documents(path: Path) -> list[dict[str, Any]]:
    return [document for document in yaml.safe_load_all(path.read_text(encoding="utf-8")) if document]


def test_metrics_endpoint_exposes_custom_series_and_is_not_rate_limited() -> None:
    service = CountingService()
    with TestClient(create_app(service, RateLimiter(limit=1, window_seconds=60))) as client:
        assert client.get("/ready").status_code == 200
        assert client.post("/predict", json={"text": "first request"}).status_code == 200
        assert client.post("/predict", json={"text": "rate limited request"}).status_code == 429
        metrics = client.get("/metrics")
        assert metrics.status_code == 200
        assert "fake_news_http_request_latency_seconds_bucket" in metrics.text
        assert "fake_news_inference_latency_seconds_bucket" in metrics.text
        assert "fake_news_inference_queue_depth" in metrics.text
        assert "fake_news_drift_queue_depth" in metrics.text
        assert "fake_news_rate_limiter_rejections_total" in metrics.text
        assert "fake_news_drift_monitoring_errors_total" in metrics.text
        assert "text/plain" in metrics.headers["content-type"]


def test_successful_warmup_is_required_for_readiness() -> None:
    service = CountingService()
    with TestClient(create_app(service, RateLimiter(limit=100, window_seconds=60))) as client:
        health = client.get("/health")
        ready = client.get("/ready")
        assert health.status_code == 200
        assert health.json()["warmup_complete"] is True
        assert ready.status_code == 200
        assert ready.json()["warmup_complete"] is True
        assert service.predict_calls >= 1


def test_failed_warmup_keeps_readiness_degraded() -> None:
    service = WarmupFailureService()
    with TestClient(create_app(service, RateLimiter(limit=100, window_seconds=60))) as client:
        health = client.get("/health")
        ready = client.get("/ready")
        assert health.status_code == 200
        assert health.json()["status"] == "degraded"
        assert health.json()["warmup_complete"] is False
        assert health.json()["warmup_error"] == "RuntimeError"
        assert ready.status_code == 503


def test_kubernetes_base_contains_secure_api_redis_hpa_and_network_policy() -> None:
    api_documents = _documents(ROOT / "k8s/base/api-deployment.yaml")
    api_deployment = next(document for document in api_documents if document["kind"] == "Deployment")
    api_container = api_deployment["spec"]["template"]["spec"]["containers"][0]
    assert api_deployment["spec"]["replicas"] == 2
    assert api_container["resources"]["limits"] == {"cpu": "1", "memory": "1Gi"}
    assert api_container["securityContext"]["readOnlyRootFilesystem"] is True
    assert {probe for probe in ("startupProbe", "livenessProbe", "readinessProbe") if probe in api_container} == {
        "startupProbe",
        "livenessProbe",
        "readinessProbe",
    }
    assert all(mount["readOnly"] for mount in api_container["volumeMounts"] if mount["name"] != "tmp")

    hpa = _documents(ROOT / "k8s/base/api-hpa.yaml")[0]
    assert hpa["apiVersion"] == "autoscaling/v2"
    assert hpa["spec"]["metrics"][0]["resource"]["target"]["averageUtilization"] == 75
    assert hpa["spec"]["minReplicas"] == 2
    assert hpa["spec"]["maxReplicas"] == 10

    redis_documents = _documents(ROOT / "k8s/base/redis-deployment.yaml")
    redis_deployment = next(document for document in redis_documents if document["kind"] == "Deployment")
    redis_container = redis_deployment["spec"]["template"]["spec"]["containers"][0]
    assert "--requirepass" in redis_container["command"]
    assert redis_container["securityContext"]["readOnlyRootFilesystem"] is True

    policy = _documents(ROOT / "k8s/base/networkpolicy.yaml")[0]
    assert policy["spec"]["podSelector"]["matchLabels"]["app"] == "fake-news-redis"
    assert policy["spec"]["ingress"][0]["from"][0]["podSelector"]["matchLabels"]["app"] == "fake-news-api"
    assert policy["spec"]["ingress"][0]["ports"] == [{"protocol": "TCP", "port": 6379}]


def test_structured_logs_are_json_and_request_correlated(capsys: Any) -> None:
    configure_logging("INFO")
    structlog.get_logger("test_day5").info("standalone_audit_event")
    standalone_lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert standalone_lines
    standalone_event = json.loads(standalone_lines[-1])
    assert standalone_event["event"] == "standalone_audit_event"
    assert standalone_event["request_id"] == "system"

    service = CountingService()
    with TestClient(create_app(service, RateLimiter(limit=100, window_seconds=60))) as client:
        response = client.post(
            "/monitoring/drift",
            headers={"X-Request-ID": "trace-day5-001"},
            json={"reference": {"a": [1, 2]}, "current": {"a": [2, 3]}},
        )
        assert response.status_code == 202
        assert response.headers["X-Request-ID"] == "trace-day5-001"
    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    events = [json.loads(line) for line in lines]
    correlated = [event for event in events if event.get("event") in {"request_started", "drift_job_enqueued", "request_completed"}]
    assert correlated
    assert all(event["request_id"] == "trace-day5-001" for event in correlated)


def test_logging_configuration_is_idempotent() -> None:
    configure_logging("INFO")
    configure_logging("INFO")
    marked = [handler for handler in logging.getLogger().handlers if getattr(handler, "_fake_news_json_handler", False)]
    assert len(marked) == 1


async def _exercise_redis_breaker() -> tuple[str, str, tuple[bool, int]]:
    import redis.asyncio as redis_asyncio
    from redis.exceptions import ConnectionError as RedisConnectionError

    class FlakyRedis:
        def __init__(self) -> None:
            self.fail = True

        async def eval(self, *args: Any) -> list[int]:
            del args
            if self.fail:
                raise RedisConnectionError("fixture connection failure")
            return [1, 5000]

        async def aclose(self) -> None:
            return None

    fake = FlakyRedis()
    original = redis_asyncio.from_url
    redis_asyncio.from_url = lambda *args, **kwargs: fake
    try:
        limiter = RedisRateLimiter("redis://fixture", failure_threshold=2, recovery_timeout_seconds=0.01)
        assert await limiter.check_async("client") == (True, 0)
        assert limiter.circuit_state == "closed"
        assert await limiter.check_async("client") == (True, 0)
        assert limiter.circuit_state == "open"
        assert await limiter.check_async("client") == (True, 0)
        await asyncio.sleep(0.02)
        fake.fail = False
        recovered = await limiter.check_async("client")
        return limiter.circuit_state, "open", recovered
    finally:
        redis_asyncio.from_url = original


def test_redis_circuit_breaker_fails_open_and_recovers() -> None:
    import asyncio

    state, opened_state, recovered = asyncio.run(_exercise_redis_breaker())
    assert opened_state == "open"
    assert state == "closed"
    assert recovered == (True, 0)


def test_kubernetes_ingress_and_service_monitor_contracts() -> None:
    ingress = _documents(ROOT / "k8s/base/ingress.yaml")[0]
    assert ingress["spec"]["ingressClassName"] == "nginx"
    assert ingress["spec"]["tls"][0]["secretName"] == "fake-news-api-tls"
    backend = ingress["spec"]["rules"][0]["http"]["paths"][0]["backend"]["service"]
    assert backend == {"name": "fake-news-api", "port": {"name": "http"}}
    assert ingress["metadata"]["annotations"]["nginx.ingress.kubernetes.io/force-ssl-redirect"] == "true"

    service_monitor = _documents(ROOT / "k8s/base/service-monitor.yaml")[0]
    assert service_monitor["apiVersion"] == "monitoring.coreos.com/v1"
    assert service_monitor["metadata"]["labels"]["release"] == "prometheus"
    assert service_monitor["spec"]["selector"]["matchLabels"] == {"app": "fake-news-api"}
    endpoint = service_monitor["spec"]["endpoints"][0]
    assert endpoint["port"] == "http"
    assert endpoint["path"] == "/metrics"
    assert endpoint["scrapeTimeout"] == "10s"


def test_kustomization_and_ci_validate_kubernetes_base() -> None:
    kustomization = yaml.safe_load((ROOT / "k8s/base/kustomization.yaml").read_text(encoding="utf-8"))
    assert set(kustomization["resources"]) == {
        "namespace.yaml",
        "api-deployment.yaml",
        "api-hpa.yaml",
        "redis-deployment.yaml",
        "networkpolicy.yaml",
        "ingress.yaml",
        "service-monitor.yaml",
    }
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "ghcr.io/yannh/kubeconform:v0.6.7" in workflow
    assert "-strict" in workflow
    assert "-kubernetes-version 1.30.0" in workflow
    assert "-schema-location file:///work/k8s/schemas/{{.ResourceKind}}{{.KindSuffix}}.json" in workflow
    assert (ROOT / "k8s/schemas/servicemonitor_v1.json").exists()
    assert "/work/k8s/base/api-deployment.yaml" in workflow
    assert "/work/k8s/base/api-hpa.yaml" in workflow
    assert "/work/k8s/base/redis-deployment.yaml" in workflow
    assert "/work/k8s/base/networkpolicy.yaml" in workflow
    assert "/work/k8s/base/ingress.yaml" in workflow
    assert "/work/k8s/base/service-monitor.yaml" in workflow
