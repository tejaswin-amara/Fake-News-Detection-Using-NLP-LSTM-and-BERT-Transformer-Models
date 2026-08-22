"""Regression checks for the lean production image dependency boundary."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_installs_serving_only_dependencies() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY requirements-runtime.txt pyproject.toml ./" in dockerfile
    assert "pip install -r requirements-runtime.txt" in dockerfile


def test_runtime_requirements_exclude_training_and_tracking_tools() -> None:
    requirements = (ROOT / "requirements-runtime.txt").read_text(encoding="utf-8")
    assert "mlflow==" not in requirements
    assert "dvc==" not in requirements
    assert "pytest==" not in requirements
    assert "torch==2.13.0" in requirements
    assert "python-multipart==0.0.32" in requirements
    assert "torchaudio==" not in requirements
    assert "torchvision==" not in requirements


def test_container_workflow_reports_high_and_blocks_critical() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "Report high and critical image vulnerabilities" in workflow
    assert "Block actionable critical image vulnerabilities" in workflow
    assert "severity: CRITICAL,HIGH" in workflow
    assert "severity: CRITICAL" in workflow
