"""Regression tests for the recognized bounded coverage-guided Python fuzzer."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_clusterfuzzlite_build_integration_is_python_and_digest_pinned() -> None:
    """Keep the coverage-guided integration reproducible and Python-specific."""
    project = yaml.safe_load((ROOT / ".clusterfuzzlite" / "project.yaml").read_text(encoding="utf-8"))
    dockerfile = (ROOT / ".clusterfuzzlite" / "Dockerfile").read_text(encoding="utf-8")
    build_script = (ROOT / ".clusterfuzzlite" / "build.sh").read_text(encoding="utf-8")

    assert project == {"language": "python"}
    assert "base-builder-python@sha256:" in dockerfile
    assert "atheris_claimreview_fuzzer.py" in build_script
    assert "pyinstaller" in build_script
    assert "raw article text" in build_script


def test_clusterfuzzlite_workflow_is_bounded_manual_and_scheduled() -> None:
    """Require a recognized immutable integration with a strict 60-second fuzz budget."""
    workflow_path = ROOT / ".github" / "workflows" / "clusterfuzzlite.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)

    assert workflow[True]["workflow_dispatch"] is None
    assert workflow[True]["schedule"] == [{"cron": "35 3 * * 1"}]
    assert workflow["permissions"] == {"contents": "read"}
    job = workflow["jobs"]["claimreview-metadata"]
    assert job["timeout-minutes"] == 15
    action_refs = [step["uses"] for step in job["steps"]]
    assert all(reference.endswith("52ecc61cb587ee99c26825a112a21abf19c7448c") for reference in action_refs)
    assert "fuzz-seconds: 60" in workflow_text
    assert "mode: batch" in workflow_text


def test_atheris_target_discards_synthetic_inputs_without_logging_or_persistence() -> None:
    """Keep the coverage-guided target privacy-safe and exclusively synthetic."""
    target = (ROOT / "fuzz" / "atheris_claimreview_fuzzer.py").read_text(encoding="utf-8")
    assert "atheris.FuzzedDataProvider" in target
    assert "synthetic fuzz input" in target
    assert "print(" not in target
    assert "write_" not in target
    assert "urlopen" not in target
