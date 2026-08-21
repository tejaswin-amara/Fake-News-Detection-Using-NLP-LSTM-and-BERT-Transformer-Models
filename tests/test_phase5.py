from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts.generate_reports import generate_report_bundle, select_best_run
from scripts.synthetic_traffic import TrafficConfig, run

ROOT = Path(__file__).resolve().parents[1]


def test_ci_workflow_contains_required_phase5_gates():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for required in [
        "pull_request",
        "actions/setup-python@v5",
        "pip install -r requirements.txt",
        "ruff check src scripts tests",
        "dvc stage list",
        "mlflow server",
        "python -m pytest -q",
        "docker/build-push-action@v6",
        "cache-from: type=gha",
        "scripts/gate_on_severity.py",
        "aquasecurity/trivy-action",
        "mypy src scripts tests",
        "bandit -r src scripts",
        "pip-audit -r requirements.txt",
        "Assert non-root image user",
    ]:
        assert required in workflow


def test_compose_declares_health_checked_api_mlflow_and_traffic_services():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    assert set(compose["services"]) == {"api", "mlflow", "traffic"}
    assert "healthcheck" in compose["services"]["api"]
    assert "healthcheck" in compose["services"]["mlflow"]
    assert compose["services"]["api"]["volumes"] == ["./artifacts:/app/artifacts:ro", "./configs:/app/configs:ro"]
    assert "scripts/synthetic_traffic.py" in compose["services"]["traffic"]["command"]
    assert compose["services"]["traffic"]["depends_on"]["api"]["condition"] == "service_healthy"
    for service in compose["services"].values():
        assert service["read_only"] is True
        assert service["cap_drop"] == ["ALL"]
        assert "no-new-privileges:true" in service["security_opt"]
        assert service["init"] is True


def test_pipeline_script_is_strict_and_ordered():
    script = (ROOT / "scripts/run_pipeline.sh").read_text(encoding="utf-8")
    assert "set -Eeuo pipefail" in script
    order = ["init_mlflow.py", "dvc repro", "src.evaluate", "export_onnx.py", "pytest", "generate_reports.py"]
    positions = [script.index(item) for item in order]
    assert positions == sorted(positions)
    assert "dvc repro" in script and "--epsilon 0.000009" in script
    assert "validate_dvc_cache" in script
    assert "retry_command" in script
    assert "MLFLOW_LOCAL_FALLBACK_URI" in script


def test_synthetic_traffic_finite_mode_hits_prediction_and_drift(monkeypatch):
    import scripts.synthetic_traffic as traffic

    calls: list[str] = []

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    def fake_urlopen(request, timeout):
        del timeout
        calls.append(request.full_url)
        return Response()

    monkeypatch.setattr(traffic, "urlopen", fake_urlopen)
    monkeypatch.setattr(traffic.time, "sleep", lambda _seconds: None)
    config = TrafficConfig("http://api", 0.0, 2, 1.0, 3)
    assert run(config) == 0
    assert calls == ["http://api/predict", "http://api/predict", "http://api/monitoring/drift", "http://api/predict"]


def test_select_best_run_respects_metric_direction():
    def make_run(run_id: str, status: str, score: float):
        return SimpleNamespace(
            info=SimpleNamespace(run_id=run_id, status=status),
            data=SimpleNamespace(metrics={"pr_auc": score}, params={}, tags={}),
        )

    runs = [make_run("low", "FINISHED", 0.3), make_run("high", "FINISHED", 0.8), make_run("running", "RUNNING", 0.99)]
    assert select_best_run(runs, "pr_auc").info.run_id == "high"
    assert select_best_run(runs, "pr_auc", maximize=False).info.run_id == "low"
    with pytest.raises(RuntimeError, match="No finalized"):
        select_best_run([make_run("running", "RUNNING", 0.99)], "pr_auc")


def test_mlflow_report_bundle_downloads_real_artifacts_and_checksums(tmp_path):
    class Entry:
        def __init__(self, path: str, is_dir: bool = False):
            self.path = path
            self.is_dir = is_dir

    class FakeClient:
        def __init__(self):
            self.run = SimpleNamespace(
                info=SimpleNamespace(run_id="run-1", status="FINISHED"),
                data=SimpleNamespace(
                    metrics={"pr_auc": 0.9, "accuracy": 0.8},
                    params={"model": "logistic_l2"},
                    tags={"mlflow.runName": "logistic_l2", "source_ids": "SRC-024,SRC-033"},
                ),
            )

        def get_experiment_by_name(self, name):
            return SimpleNamespace(experiment_id="exp-1", name=name)

        def search_runs(self, _ids, order_by=None):
            del order_by
            return [self.run]

        def list_artifacts(self, _run_id, prefix=""):
            del prefix
            return [Entry("reliability.png"), Entry("roc_pr.png"), Entry("shap_summary.png")]

        def download_artifacts(self, _run_id, artifact_path, dst_path):
            destination = Path(dst_path) / artifact_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((artifact_path + "-real-artifact").encode("utf-8"))
            return str(destination)

    summary = generate_report_bundle("file:///tmp/mlruns", "fake-news-detection", tmp_path, client=FakeClient())
    assert summary["best_run"]["run_id"] == "run-1"
    assert summary["best_run"]["metrics"]["pr_auc"] == 0.9
    assert summary["plots"]["reliability.png"]["status"] == "available"
    assert summary["plots"]["shap_summary.png"]["status"] == "available"
    assert (tmp_path / "best_model_summary.json").exists()
    manifest = json.loads((tmp_path / "report_manifest.json").read_text(encoding="utf-8"))
    assert manifest["best_run_id"] == "run-1"
    assert all("sha256" in entry for entry in manifest["entries"])


def test_final_documentation_contains_required_phase5_contracts():
    model_card = (ROOT / "docs/model_cards.md").read_text(encoding="utf-8")
    dataset_card = (ROOT / "docs/dataset_card.md").read_text(encoding="utf-8")
    mathematics = (ROOT / "docs/mathematical_formulation.md").read_text(encoding="utf-8")
    compliance = (ROOT / "docs/compliance_matrix.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for text, terms in [
        (model_card, ["Out-of-scope use", "Ethical considerations", "Brier score", "bert-base-uncased"]),
        (dataset_card, ["WELFake", "0 = real", "1 = fake", "Privacy, ethics, and security"]),
        (mathematics, ["LSTM", "scaled dot-product attention", "density-reachable", "Isolation Forest", "PSI"]),
        (compliance, ["CO6 / M6", "Phase 5 completion matrix", "Complete"]),
        (readme, ["100% implemented", "docker-compose.yml", "scripts/run_pipeline.sh", "Complete through Phase 5"]),
    ]:
        for term in terms:
            assert term in text


def test_readme_retains_all_visible_reference_numbers():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    references = [line for line in readme.splitlines() if line.startswith(tuple(f"{i}." for i in range(1, 37)))]
    assert len(references) == 36
