"""Regression tests for provider-neutral production deployment gates."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from pytest import CaptureFixture

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "verify_production_readiness.py"
SPEC = importlib.util.spec_from_file_location("verify_production_readiness", MODULE_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def valid_contract() -> dict[str, str]:
    """Return only synthetic, non-secret values for contract unit tests."""
    digest = "sha256:" + "a" * 64
    checksum = "b" * 64
    return {
        "DEPLOYMENT_ENVIRONMENT": "production",
        "RELEASE_IMAGE_DIGEST": digest,
        "KUBERNETES_NAMESPACE": "ml-production",
        "INGRESS_HOST": "verify.example.invalid",
        "TLS_SECRET_NAME": "api-tls",
        "SECRET_MANAGER_REFERENCE": "manager://production/fake-news",
        "MODEL_ARTIFACT_URI": "artifact://models/fake-news/v1",
        "MODEL_ARTIFACT_SHA256": checksum,
        "MODEL_ARTIFACT_SIGNATURE_REFERENCE": "manager://signatures/fake-news/v1",
        "REDIS_SECRET_REFERENCE": "manager://redis/fake-news",
        "PROMETHEUS_OWNER": "platform-observability",
        "ON_CALL_OWNER": "ml-service-oncall",
        "STAGING_BASE_URL": "https" + "://staging.example.invalid",
        "CAPACITY_TEST_AUTHORIZATION": "yes",
        "ROLLBACK_IMAGE_DIGEST": digest,
        "ROLLBACK_MODEL_ARTIFACT_SHA256": checksum,
    }


def test_contract_requires_complete_owner_evidence_without_echoing_values() -> None:
    """Blank and example fields must block preflight, while valid structured evidence passes."""
    assert VALIDATOR.validate_contract(valid_contract()) == []
    unsafe = valid_contract() | {"INGRESS_HOST": "fake-news.example.com", "CAPACITY_TEST_AUTHORIZATION": "no"}
    issues = VALIDATOR.validate_contract(unsafe)
    assert "contract key contains a forbidden placeholder: INGRESS_HOST" in issues
    assert "CAPACITY_TEST_AUTHORIZATION must be yes after documented owner approval" in issues
    assert "fake-news.example.com" not in "\n".join(issues)


def test_base_manifests_are_explicitly_not_a_production_release(tmp_path: Path) -> None:
    """Keep example image and ingress settings from being mistaken for deployable production values."""
    manifest = tmp_path / "rendered.yaml"
    manifest.write_text(
        "\n---\n".join(
            (ROOT / "k8s" / "base" / path).read_text(encoding="utf-8")
            for path in (
                "api-deployment.yaml",
                "api-hpa.yaml",
                "ingress.yaml",
                "networkpolicy.yaml",
                "service-monitor.yaml",
            )
        ),
        encoding="utf-8",
    )
    issues = VALIDATOR.validate_manifests(manifest)
    assert "api image must be pinned to an immutable sha256 digest" in issues
    assert "Deployment must use a no-unavailability rolling-update strategy" not in issues


def test_release_contract_template_is_sanitized_and_intentionally_fails() -> None:
    """The tracked template documents fields without ever becoming production evidence."""
    template = ROOT / "deploy" / "production-release-contract.example.env"
    contract = VALIDATOR.parse_contract(template)
    assert "RELEASE_IMAGE_DIGEST" in contract
    assert VALIDATOR.validate_contract(contract)
    assert "REDIS_PASSWORD" not in template.read_text(encoding="utf-8")


def test_preflight_cli_never_echoes_private_contract_values(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    """A failing preflight must report only a rule count, never an owner-held value."""
    contract = tmp_path / "contract.env"
    manifest = tmp_path / "manifest.yaml"
    contract.write_text("DEPLOYMENT_ENVIRONMENT=not-production\n", encoding="utf-8")
    manifest.write_text("apiVersion: v1\nkind: ConfigMap\n", encoding="utf-8")
    assert VALIDATOR.main(["--contract", str(contract), "--manifest", str(manifest)]) == 1
    captured = capsys.readouterr().err
    assert "non-sensitive rule(s)" in captured
    assert "not-production" not in captured


def test_production_documentation_and_source_registers_are_synchronized() -> None:
    """Preserve the no-deployment gate and cited operational guidance."""
    readiness = (ROOT / "docs" / "deployment" / "production-readiness.md").read_text(encoding="utf-8")
    adr = (ROOT / "docs" / "ADR" / "0007-production-deployment-boundary.md").read_text(encoding="utf-8")
    sources = (ROOT / "docs" / "sources.md").read_text(encoding="utf-8")
    sources_yaml = (ROOT / "docs" / "sources.yaml").read_text(encoding="utf-8")
    assert "production deployment not yet authorized" in readiness.lower()
    assert "existing or newly provisioned kubernetes cluster" in readiness.lower()
    assert "does not execute production deployment" in readiness.lower()
    assert "do not identify a cloud account" in adr.lower()
    assert "SRC-057" in sources
    assert "SRC-057" in sources_yaml
    rollout = (ROOT / "docs" / "deployment" / "production-rollout.md").read_text(encoding="utf-8")
    assert "does not authorize a deployment" in rollout.lower()
    assert "raw article text" in rollout.lower()
