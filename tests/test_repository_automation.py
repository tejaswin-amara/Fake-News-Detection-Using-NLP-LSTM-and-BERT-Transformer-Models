"""Regression tests for Deliverables 4–7 repository controls."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    """Read a repository text fixture using the project root."""
    return (ROOT / path).read_text(encoding="utf-8")


def test_configuration_and_devcontainer_are_safe_and_parseable() -> None:
    """Keep cloud-development settings pinned, parseable, and secret-free."""
    for path in (".gitattributes", ".editorconfig", ".github/CODEOWNERS"):
        assert (ROOT / path).is_file(), f"Missing repository configuration: {path}"

    devcontainer = json.loads(read(".devcontainer/devcontainer.json"))
    assert "3.11" in devcontainer["image"]
    assert "requirements.txt" in devcontainer["postCreateCommand"]
    assert devcontainer["containerEnv"]["PYTHONPATH"] == "${containerWorkspaceFolder}"

    environment = read(".env.example")
    assert environment.count("PACKAGE_MANIFEST=") == 1
    assert "replace-with-a-long-random-url-safe-secret" not in environment
    assert "REPLACE_WITH_A_LONG_RANDOM_URL_SAFE_SECRET" in environment


def test_issue_forms_and_automation_workflows_are_parseable_and_guarded() -> None:
    """Require public forms and safe-by-default side-effect workflow activation."""
    bug_form = yaml.safe_load(read(".github/ISSUE_TEMPLATE/bug_report.yml"))
    feature_form = yaml.safe_load(read(".github/ISSUE_TEMPLATE/feature_request.yml"))
    assert bug_form["labels"] == ["bug"]
    assert feature_form["labels"] == ["enhancement"]

    for path in (
        ".github/dependabot.yml",
        ".github/labeler.yml",
        ".github/workflows/ci.yml",
        ".github/workflows/clusterfuzzlite.yml",
        ".github/workflows/codeql.yml",
        ".github/workflows/fuzz.yml",
        ".github/workflows/release.yml",
        ".github/workflows/scorecards.yml",
        ".github/workflows/labeler.yml",
    ):
        assert isinstance(yaml.safe_load(read(path)), dict), f"Invalid YAML: {path}"

    ci_workflow = read(".github/workflows/ci.yml")
    assert "--cov-fail-under=95" in ci_workflow
    assert "container-build-and-scan" in ci_workflow

    codeql_workflow = read(".github/workflows/codeql.yml")
    assert "github/codeql-action/init@db488ddef3bf6cb639b32c2e9a7c0a7ea8271d28" in codeql_workflow
    assert "github/codeql-action/analyze@db488ddef3bf6cb639b32c2e9a7c0a7ea8271d28" in codeql_workflow
    assert "security-events: write" in codeql_workflow

    release_workflow = read(".github/workflows/release.yml")
    assert "push:" in release_workflow
    assert "branches: [main]" in release_workflow
    assert "workflow_run:" not in release_workflow
    assert "permissions: read-all" in release_workflow
    assert "contents: write" in release_workflow
    assert "ENABLE_SEMANTIC_RELEASE == 'true'" in release_workflow

    labeler_workflow = read(".github/workflows/labeler.yml")
    assert "pull_request_target:" in labeler_workflow
    assert "ENABLE_PATH_LABELER == 'true'" in labeler_workflow
    assert "actions/checkout" not in labeler_workflow

    fuzz_workflow = read(".github/workflows/fuzz.yml")
    assert "workflow_dispatch:" in fuzz_workflow
    assert "schedule:" in fuzz_workflow
    assert 'cron: "20 3 * * 1"' in fuzz_workflow
    assert "timeout-minutes: 5" in fuzz_workflow
    assert "retention-days: 7" in fuzz_workflow

    clusterfuzzlite_workflow = read(".github/workflows/clusterfuzzlite.yml")
    assert "google/clusterfuzzlite/actions/build_fuzzers@52ecc61cb587ee99c26825a112a21abf19c7448c" in clusterfuzzlite_workflow
    assert "google/clusterfuzzlite/actions/run_fuzzers@52ecc61cb587ee99c26825a112a21abf19c7448c" in clusterfuzzlite_workflow


def test_workflow_actions_and_python_base_image_are_immutable() -> None:
    """Require full action commits and matching Python image digests."""
    workflow_paths = (
        ".github/workflows/ci.yml",
        ".github/workflows/clusterfuzzlite.yml",
        ".github/workflows/codeql.yml",
        ".github/workflows/fuzz.yml",
        ".github/workflows/release.yml",
        ".github/workflows/scorecards.yml",
        ".github/workflows/labeler.yml",
    )
    action_pattern = re.compile(r"^\s*uses:\s*[^@\s]+@([0-9a-f]{40})(?:\s+#.*)?$", re.MULTILINE)

    for path in workflow_paths:
        workflow = read(path)
        action_lines = [line for line in workflow.splitlines() if line.strip().startswith("uses:")]
        assert action_lines, f"Expected action references in {path}"
        assert len(action_pattern.findall(workflow)) == len(action_lines), path

    dockerfile = read("Dockerfile")
    base_digests = re.findall(r"FROM python:3\.11-slim@sha256:([0-9a-f]{64})", dockerfile)
    assert len(base_digests) == 2
    assert len(set(base_digests)) == 1


def test_scorecard_remediated_dependency_pins_cannot_be_downgraded() -> None:
    """Preserve the minimum versions that resolve verified Scorecard advisories."""
    development_pins = dict(
        line.split("==", maxsplit=1)
        for line in read("requirements.txt").splitlines()
        if "==" in line and not line.lstrip().startswith("#")
    )

    expected_pins = {
        "cryptography": "49.0.0",
        "datasets": "5.0.1",
        "fastapi": "0.141.1",
        "lightgbm": "4.6.0",
        "mlflow": "3.15.1",
        "nltk": "3.10.3",
        "onnx": "1.22.0  # Compatible with skl2onnx 1.20.0",
        "pytest": "9.0.3",
        "python-multipart": "0.0.32",
        "torch": "2.13.0",
    }
    assert {name: development_pins[name] for name in expected_pins} == expected_pins
    assert "torchaudio" not in development_pins
    assert "torchvision" not in development_pins

    runtime_pins = dict(
        line.split("==", maxsplit=1)
        for line in read("requirements-runtime.txt").splitlines()
        if "==" in line and not line.lstrip().startswith("#")
    )
    assert {
        "cryptography": runtime_pins["cryptography"],
        "python-multipart": runtime_pins["python-multipart"],
        "torch": runtime_pins["torch"],
    } == {
        "cryptography": "49.0.0",
        "python-multipart": "0.0.32",
        "torch": "2.13.0",
    }
    assert "torchaudio" not in runtime_pins
    assert "torchvision" not in runtime_pins

    pyproject = read("pyproject.toml")
    assert 'tracking = ["mlflow==3.15.1"]' in pyproject
    assert '"pytest==9.0.3"' in pyproject


def test_automated_python_installs_use_complete_platform_hash_locks() -> None:
    """Require complete hash checking for every Scorecard-alerted pip command."""
    lock_paths = (
        "requirements/locks/development-py311-manylinux_2_28.txt",
        "requirements/locks/runtime-py311-manylinux_2_28.txt",
        "requirements/locks/fuzz-py311-manylinux_2_28.txt",
    )
    for path in lock_paths:
        lock = read(path)
        assert "--hash=sha256:" in lock, path
        assert "manylinux_2_28" in lock, path

    ci_workflow = read(".github/workflows/ci.yml")
    fuzz_workflow = read(".github/workflows/fuzz.yml")
    clusterfuzzlite_build = read(".clusterfuzzlite/build.sh")
    dockerfile = read("Dockerfile")

    for automated_install in (ci_workflow, fuzz_workflow, clusterfuzzlite_build, dockerfile):
        assert "--require-hashes" in automated_install
        assert "--only-binary=:all:" in automated_install
        assert "pip install --upgrade pip" not in automated_install

    assert "development-py311-manylinux_2_28.txt" in ci_workflow
    assert "fuzz-py311-manylinux_2_28.txt" in fuzz_workflow
    assert "fuzz-py311-manylinux_2_28.txt" in clusterfuzzlite_build
    assert "runtime-py311-manylinux_2_28.txt" in dockerfile
    assert "requirements/fuzz.in" in read("scripts/generate_hash_locks.sh")
    assert "SRC-053" in read("docs/security/hash-lock-maintenance.md")


def test_agent_guidance_and_seo_blueprint_preserve_project_boundaries() -> None:
    """Ensure agents and discovery guidance retain quality and classification limits."""
    for path in ("CLAUDE.md", ".cursorrules", ".github/copilot-instructions.md"):
        content = read(path).lower()
        assert "split-before-fit" in content
        assert "raw article text" in content
        assert "source" in content

    blueprint = read("github-seo-growth-strategy.md")
    description = (
        "Reproducible fake-news text classification with NLP, BiLSTM, BERT, DVC, MLflow, "
        "FastAPI, ONNX, monitoring, Kubernetes, and CI/CD quality gates for research use."
    )
    assert description in blueprint
    assert len(description) == 160

    topics_start = blueprint.index("fake-news-detection\n")
    topics_end = blueprint.index("```", topics_start)
    topics = blueprint[topics_start:topics_end].strip().splitlines()
    assert len(topics) == 20
    assert all(topic == topic.lower() and " " not in topic for topic in topics)
    assert "not independent fact verification" in blueprint.lower()


def test_scorecard_remediation_ledger_preserves_evidence_and_open_dispositions() -> None:
    """Keep final remediation reporting explicit about resolved and owner-controlled work."""
    ledger = read("docs/security/code-scanning-remediation.md")
    assert "32565674353" in ledger
    assert "PYSEC-2026-3552" in ledger
    assert "FuzzingID" in ledger
    assert "no SARIF finding was filtered or dismissed" in ledger
    assert "owner action" in ledger.lower()

    sources = read("docs/sources.md")
    sources_yaml = read("docs/sources.yaml")
    assert "SRC-052" in sources
    assert "SRC-052" in sources_yaml
    assert "SRC-053" in sources
    assert "SRC-053" in sources_yaml
