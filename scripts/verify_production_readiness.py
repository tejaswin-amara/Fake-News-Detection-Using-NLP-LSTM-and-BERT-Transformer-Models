#!/usr/bin/env python3
"""Validate a non-secret release contract before an owner-authorized Kubernetes rollout.

The validator operates only on a sanitized environment-style contract and rendered
Kubernetes YAML. It never prints contract values, parses raw article content, or
contacts a cluster, registry, secret manager, or external endpoint.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REQUIRED_CONTRACT_KEYS = (
    "DEPLOYMENT_ENVIRONMENT",
    "RELEASE_IMAGE_DIGEST",
    "KUBERNETES_NAMESPACE",
    "INGRESS_HOST",
    "TLS_SECRET_NAME",
    "SECRET_MANAGER_REFERENCE",
    "MODEL_ARTIFACT_URI",
    "MODEL_ARTIFACT_SHA256",
    "MODEL_ARTIFACT_SIGNATURE_REFERENCE",
    "REDIS_SECRET_REFERENCE",
    "PROMETHEUS_OWNER",
    "ON_CALL_OWNER",
    "STAGING_BASE_URL",
    "CAPACITY_TEST_AUTHORIZATION",
    "ROLLBACK_IMAGE_DIGEST",
    "ROLLBACK_MODEL_ARTIFACT_SHA256",
)
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_PLACEHOLDER_TOKENS = (
    "change-me",
    "example.com",
    "replace-with",
    "replace_me",
    "todo",
    "phase5",
)
REQUIRED_SECRET_ENVIRONMENT_KEYS = {
    "ARTIFACT_PUBLIC_KEY_B64",
    "REDIS_URL",
    "REDIS_PASSWORD",
}


def parse_contract(path: Path) -> dict[str, str]:
    """Parse KEY=VALUE lines while retaining no values outside local memory."""
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError("contract contains a non-comment line without an equals sign")
        key, value = line.split("=", maxsplit=1)
        if not key or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            raise ValueError("contract contains an invalid key name")
        result[key] = value.strip()
    return result


def _has_forbidden_placeholder(value: str) -> bool:
    normalized = value.lower()
    return any(token in normalized for token in FORBIDDEN_PLACEHOLDER_TOKENS)


def validate_contract(contract: dict[str, str]) -> list[str]:
    """Return redacted validation failures for the release contract."""
    issues: list[str] = []
    missing = [key for key in REQUIRED_CONTRACT_KEYS if not contract.get(key)]
    issues.extend(f"missing required contract key: {key}" for key in missing)

    for key in REQUIRED_CONTRACT_KEYS:
        value = contract.get(key, "")
        if value and _has_forbidden_placeholder(value):
            issues.append(f"contract key contains a forbidden placeholder: {key}")

    if contract.get("DEPLOYMENT_ENVIRONMENT") != "production":
        issues.append("DEPLOYMENT_ENVIRONMENT must be production")
    if contract.get("CAPACITY_TEST_AUTHORIZATION") != "yes":
        issues.append("CAPACITY_TEST_AUTHORIZATION must be yes after documented owner approval")
    for key in ("RELEASE_IMAGE_DIGEST", "ROLLBACK_IMAGE_DIGEST"):
        if contract.get(key) and not DIGEST_PATTERN.fullmatch(contract[key]):
            issues.append(f"{key} must be an immutable sha256 image digest")
    for key in ("MODEL_ARTIFACT_SHA256", "ROLLBACK_MODEL_ARTIFACT_SHA256"):
        if contract.get(key) and not SHA256_PATTERN.fullmatch(contract[key]):
            issues.append(f"{key} must be a 64-character lowercase SHA-256 value")
    if contract.get("INGRESS_HOST") and "://" in contract["INGRESS_HOST"]:
        issues.append("INGRESS_HOST must be a host name, not a URL")
    if contract.get("STAGING_BASE_URL") and not contract["STAGING_BASE_URL"].startswith("https://"):
        issues.append("STAGING_BASE_URL must use HTTPS")
    return issues


def _documents(path: Path) -> list[dict[str, Any]]:
    documents = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    return [document for document in documents if isinstance(document, dict)]


def _find_document(documents: list[dict[str, Any]], kind: str, name: str) -> dict[str, Any] | None:
    for document in documents:
        metadata = document.get("metadata", {})
        if document.get("kind") == kind and metadata.get("name") == name:
            return document
    return None


def validate_manifests(path: Path) -> list[str]:
    """Validate rendered production manifests without executing them."""
    documents = _documents(path)
    issues: list[str] = []
    deployment = _find_document(documents, "Deployment", "fake-news-api")
    hpa = _find_document(documents, "HorizontalPodAutoscaler", "fake-news-api")
    ingress = _find_document(documents, "Ingress", "fake-news-api")
    network_policy = _find_document(documents, "NetworkPolicy", "fake-news-redis-isolation")
    service_monitor = _find_document(documents, "ServiceMonitor", "fake-news-api")
    for label, document in (
        ("Deployment/fake-news-api", deployment),
        ("HorizontalPodAutoscaler/fake-news-api", hpa),
        ("Ingress/fake-news-api", ingress),
        ("NetworkPolicy/fake-news-redis-isolation", network_policy),
        ("ServiceMonitor/fake-news-api", service_monitor),
    ):
        if document is None:
            issues.append(f"missing required rendered manifest: {label}")
    if issues:
        return issues

    assert deployment is not None
    assert hpa is not None
    assert ingress is not None
    assert service_monitor is not None
    pod_spec = deployment.get("spec", {}).get("template", {}).get("spec", {})
    containers = pod_spec.get("containers", [])
    api_container = next((item for item in containers if item.get("name") == "api"), None)
    if not isinstance(api_container, dict):
        return ["Deployment/fake-news-api must define an api container"]
    image = str(api_container.get("image", ""))
    if "@sha256:" not in image or not DIGEST_PATTERN.search(image):
        issues.append("api image must be pinned to an immutable sha256 digest")
    security_context = api_container.get("securityContext", {})
    if security_context.get("allowPrivilegeEscalation") is not False:
        issues.append("api container must forbid privilege escalation")
    if security_context.get("readOnlyRootFilesystem") is not True:
        issues.append("api container must use a read-only root filesystem")
    if "ALL" not in security_context.get("capabilities", {}).get("drop", []):
        issues.append("api container must drop all Linux capabilities")
    if pod_spec.get("automountServiceAccountToken") is not False:
        issues.append("api Pod must disable service-account token automounting")
    if pod_spec.get("securityContext", {}).get("seccompProfile", {}).get("type") != "RuntimeDefault":
        issues.append("api Pod must use the RuntimeDefault seccomp profile")
    for probe_name, expected_path in (
        ("startupProbe", "/health"),
        ("livenessProbe", "/health"),
        ("readinessProbe", "/ready"),
    ):
        actual_path = api_container.get(probe_name, {}).get("httpGet", {}).get("path")
        if actual_path != expected_path:
            issues.append(f"api container requires {probe_name} on {expected_path}")
    resources = api_container.get("resources", {})
    if not resources.get("requests", {}).get("cpu") or not resources.get("requests", {}).get("memory"):
        issues.append("api container must declare CPU and memory requests")
    if not resources.get("limits", {}).get("cpu") or not resources.get("limits", {}).get("memory"):
        issues.append("api container must declare CPU and memory limits")
    environment = {item.get("name"): item for item in api_container.get("env", []) if item.get("name")}
    for key in REQUIRED_SECRET_ENVIRONMENT_KEYS:
        source = environment.get(key, {}).get("valueFrom", {}).get("secretKeyRef")
        if not isinstance(source, dict) or not source.get("name") or not source.get("key"):
            issues.append(f"{key} must be supplied by a Secret reference")
    if environment.get("REQUIRE_SIGNED_ARTIFACT", {}).get("value") != "true":
        issues.append("REQUIRE_SIGNED_ARTIFACT must remain true")

    strategy = deployment.get("spec", {}).get("strategy", {})
    rolling_update = strategy.get("rollingUpdate", {})
    if strategy.get("type") != "RollingUpdate" or rolling_update.get("maxUnavailable") != 0:
        issues.append("Deployment must use a no-unavailability rolling-update strategy")
    if deployment.get("spec", {}).get("revisionHistoryLimit", 0) < 2:
        issues.append("Deployment must retain at least two rollout revisions")

    hpa_spec = hpa.get("spec", {})
    if hpa_spec.get("minReplicas", 0) < 2 or hpa_spec.get("maxReplicas", 0) <= hpa_spec.get("minReplicas", 0):
        issues.append("HPA must preserve at least two replicas and a higher maximum")
    hosts = [rule.get("host", "") for rule in ingress.get("spec", {}).get("rules", [])]
    if not hosts or any(not host or _has_forbidden_placeholder(host) for host in hosts):
        issues.append("Ingress must use a real non-placeholder host")
    tls_entries = ingress.get("spec", {}).get("tls", [])
    tls_hosts = [host for entry in tls_entries for host in entry.get("hosts", [])]
    if not tls_entries or not tls_entries[0].get("secretName") or set(hosts) - set(tls_hosts):
        issues.append("Ingress must bind every route host to a TLS secret")
    endpoints = service_monitor.get("spec", {}).get("endpoints", [])
    if not any(endpoint.get("path") == "/metrics" for endpoint in endpoints):
        issues.append("ServiceMonitor must scrape the /metrics endpoint")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True, help="Sanitized release contract file")
    parser.add_argument("--manifest", type=Path, required=True, help="Rendered Kubernetes YAML to validate")
    arguments = parser.parse_args(argv)
    if not arguments.contract.is_file() or not arguments.manifest.is_file():
        print("readiness validation requires readable contract and manifest files", file=sys.stderr)
        return 2
    try:
        issues = validate_contract(parse_contract(arguments.contract)) + validate_manifests(arguments.manifest)
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"readiness validation failed safely: {type(error).__name__}", file=sys.stderr)
        return 2
    if issues:
        print(
            f"production readiness preflight failed: {len(issues)} non-sensitive rule(s) did not pass. "
            "Review the private contract and docs/deployment/production-readiness.md.",
            file=sys.stderr,
        )
        return 1
    print("production readiness preflight passed; owner approval and rollout execution remain external.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
