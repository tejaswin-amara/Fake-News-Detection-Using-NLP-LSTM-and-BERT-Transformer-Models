"""Generate a provenance-preserving report bundle from finalized MLflow runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tracking import resolve_tracking_uri


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _run_status(run: Any) -> str:
    return str(getattr(getattr(run, "info", None), "status", "")).upper()


def select_best_run(runs: Iterable[Any], metric: str, maximize: bool = True) -> Any:
    candidates = [run for run in runs if _run_status(run) == "FINISHED" and metric in run.data.metrics]
    if not candidates:
        raise RuntimeError(f"No finalized MLflow run contains metric '{metric}'")
    return sorted(candidates, key=lambda run: float(run.data.metrics[metric]), reverse=maximize)[0]


def _list_artifacts(client: Any, run_id: str, prefix: str = "") -> list[str]:
    paths: list[str] = []
    for entry in client.list_artifacts(run_id, prefix):
        if entry.is_dir:
            paths.extend(_list_artifacts(client, run_id, entry.path))
        else:
            paths.append(entry.path)
    return paths


def _copy_downloaded_artifacts(client: Any, run_id: str, output_dir: Path) -> list[Path]:
    run_dir = output_dir / "mlflow_runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for artifact_path in _list_artifacts(client, run_id):
        downloaded = Path(client.download_artifacts(run_id, artifact_path, str(run_dir)))
        destination = run_dir / artifact_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if downloaded.resolve() != destination.resolve() and downloaded.exists():
            shutil.copy2(downloaded, destination)
        copied.append(destination)
    return copied


def _stable_plot_name(path: Path) -> str | None:
    name = path.name.lower()
    mappings = {
        "reliability.png": "reliability.png",
        "calibration_comparison.png": "calibration_comparison.png",
        "roc_pr.png": "roc_pr.png",
        "confusion_matrix.png": "confusion_matrix.png",
        "shap_summary.png": "shap_summary.png",
        "shap_summary_plot.png": "shap_summary.png",
    }
    return mappings.get(name)


def _generate_shap_summary(run: Any, output_dir: Path, evaluation_data: Path) -> Path | None:
    artifact_value = run.data.params.get("artifact")
    if not artifact_value:
        return None
    artifact_path = Path(str(artifact_value))
    if not artifact_path.exists() or not evaluation_data.exists():
        return None
    try:
        import joblib
        import matplotlib
        import pandas as pd
        import shap  # type: ignore

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        payload = joblib.load(artifact_path)
        model = payload["model"] if isinstance(payload, dict) else payload
        estimator = getattr(model, "estimator", None)
        pipeline = getattr(model, "text_pipeline", None)
        if estimator is None or pipeline is None:
            return None
        frame = pd.read_csv(evaluation_data)
        features = pipeline.transform(frame["content"].fillna("").tolist())
        dense = features.toarray() if hasattr(features, "toarray") else np.asarray(features)
        sample = dense[:1000]
        if hasattr(estimator, "coef_"):
            explainer = shap.LinearExplainer(estimator, sample)
        else:
            explainer = shap.TreeExplainer(estimator)
        values = explainer.shap_values(sample)
        if isinstance(values, list):
            values = values[-1]
        values = getattr(values, "values", values)
        values_array = np.asarray(values)
        if values_array.ndim == 3:
            values_array = values_array[:, :, -1]
        importance = np.abs(values_array).mean(axis=0).reshape(-1)
        vectorizer = getattr(pipeline, "vectorizer", None)
        names = vectorizer.get_feature_names_out() if vectorizer is not None else np.arange(len(importance)).astype(str)
        top = np.argsort(importance)[-20:]
        figure, axis = plt.subplots(figsize=(9, 6))
        axis.barh(np.asarray(names)[top], importance[top])
        axis.set_title("SHAP summary (mean absolute attribution)")
        axis.set_xlabel("mean absolute SHAP value")
        figure.tight_layout()
        output = output_dir / "shap_summary.png"
        figure.savefig(output, dpi=160)
        plt.close(figure)
        return output
    except (ImportError, KeyError, OSError, ValueError, TypeError):
        return None


def _copy_stable_plots(artifacts: list[Path], output_dir: Path) -> dict[str, dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    expected = {
        "reliability.png": "calibration reliability diagram",
        "calibration_comparison.png": "calibration comparison",
        "roc_pr.png": "ROC/PR curve",
        "confusion_matrix.png": "confusion matrix",
        "shap_summary.png": "SHAP summary plot",
    }
    result: dict[str, dict[str, Any]] = {}
    by_name = {path.name.lower(): path for path in artifacts if path.exists()}
    for stable_name, description in expected.items():
        source = by_name.get(stable_name.lower())
        if source is None and stable_name == "shap_summary.png":
            source = by_name.get("shap_summary_plot.png")
        if source is None:
            result[stable_name] = {"status": "unavailable", "description": description, "reason": "not logged by selected run"}
            continue
        destination = output_dir / stable_name
        shutil.copy2(source, destination)
        result[stable_name] = {
            "status": "available",
            "description": description,
            "path": str(destination),
            "sha256": _sha256(destination),
            "source_artifact": str(source),
        }
    return result


def generate_report_bundle(
    tracking_uri: str,
    experiment_name: str,
    output_dir: str | Path,
    primary_metric: str = "pr_auc",
    maximize: bool = True,
    client: Any | None = None,
    evaluation_data: str | Path = "data/processed/test.csv",
) -> dict[str, Any]:
    try:
        import mlflow  # type: ignore
        from mlflow.tracking import MlflowClient  # type: ignore
    except ImportError as exc:
        raise RuntimeError("MLflow is required to generate finalized run reports") from exc
    resolved_tracking_uri, _ = resolve_tracking_uri(tracking_uri)
    mlflow.set_tracking_uri(resolved_tracking_uri)
    active_client = client or MlflowClient(tracking_uri=resolved_tracking_uri)
    experiment = active_client.get_experiment_by_name(experiment_name)
    if experiment is None:
        raise RuntimeError(f"MLflow experiment does not exist: {experiment_name}")
    runs = active_client.search_runs([experiment.experiment_id], order_by=[f"metrics.{primary_metric} DESC"] if maximize else [f"metrics.{primary_metric} ASC"])
    best = select_best_run(runs, primary_metric, maximize=maximize)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    artifacts = _copy_downloaded_artifacts(active_client, best.info.run_id, destination)
    generated_shap = _generate_shap_summary(best, destination, Path(evaluation_data))
    if generated_shap is not None:
        artifacts.append(generated_shap)
    plots = _copy_stable_plots(artifacts, destination)
    summary = {
        "experiment_name": experiment.name,
        "experiment_id": experiment.experiment_id,
        "tracking_uri": resolved_tracking_uri,
        "selection": {"metric": primary_metric, "direction": "maximize" if maximize else "minimize"},
        "best_run": {
            "run_id": best.info.run_id,
            "status": _run_status(best),
            "model_name": best.data.tags.get("mlflow.runName", best.data.params.get("model", "unknown")),
            "metrics": dict(best.data.metrics),
            "params": dict(best.data.params),
            "tags": dict(best.data.tags),
        },
        "artifact_root": str(destination / "mlflow_runs" / best.info.run_id),
        "plots": plots,
        "source_ids": best.data.tags.get("source_ids", ["SRC-024", "SRC-025", "SRC-029", "SRC-033"]),
        "test_data_used_for_selection": False,
        "generated_from_executed_run": True,
    }
    summary_path = destination / "best_model_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    manifest_entries = []
    for path in [*artifacts, summary_path, *[destination / name for name, value in plots.items() if value.get("status") == "available"]]:
        if path.exists():
            manifest_entries.append({"path": str(path), "sha256": _sha256(path), "run_id": best.info.run_id})
    manifest = {"best_run_id": best.info.run_id, "entries": manifest_entries, "plots": plots, "summary": str(summary_path)}
    (destination / "report_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate reports from finalized MLflow runs")
    parser.add_argument("--tracking-uri", default="mlruns")
    parser.add_argument("--experiment-name", default="fake-news-detection")
    parser.add_argument("--output-dir", default="reports")
    parser.add_argument("--primary-metric", default="pr_auc")
    parser.add_argument("--direction", choices=["maximize", "minimize"], default="maximize")
    parser.add_argument("--evaluation-data", default="data/processed/test.csv")
    args = parser.parse_args()
    summary = generate_report_bundle(
        args.tracking_uri,
        args.experiment_name,
        args.output_dir,
        args.primary_metric,
        args.direction == "maximize",
        evaluation_data=args.evaluation_data,
    )
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
