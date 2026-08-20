"""Optional MLflow experiment-tracking integration.

References SRC-033 and SRC-036 in docs/sources.md. Tracking is disabled by
default so the classical/API paths remain usable without a tracking server.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def _local_uri(value: str | Path) -> str:
    """Convert a local path to a stable MLflow file URI and create it."""
    candidate = str(value)
    parsed = urlparse(candidate)
    if parsed.scheme:
        return candidate
    path = Path(candidate).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path.as_uri()


def initialize_tracking(
    tracking_uri: str = "mlruns",
    experiment_name: str = "fake-news-detection",
    artifact_location: str | None = None,
) -> dict[str, str]:
    """Initialize or reuse a local/remote MLflow experiment idempotently."""
    try:
        import mlflow  # type: ignore
    except ImportError as exc:
        raise RuntimeError("MLflow tracking requires the mlflow package") from exc

    resolved_uri = _local_uri(tracking_uri)
    resolved_artifacts = _local_uri(artifact_location) if artifact_location else None
    mlflow.set_tracking_uri(resolved_uri)
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(
            experiment_name,
            artifact_location=resolved_artifacts,
        )
        experiment = mlflow.get_experiment(experiment_id)
    mlflow.set_experiment(experiment_name)
    return {
        "tracking_uri": resolved_uri,
        "experiment_name": experiment.name,
        "experiment_id": experiment.experiment_id,
        "artifact_location": str(experiment.artifact_location),
    }


@contextmanager
def experiment_run(
    enabled: bool = False,
    tracking_uri: str = "mlruns",
    experiment_name: str = "fake-news-detection",
    run_name: str | None = None,
    artifact_location: str | None = None,
) -> Iterator[Any]:
    if not enabled:
        yield None
        return
    import mlflow  # type: ignore

    initialize_tracking(
        tracking_uri=tracking_uri,
        experiment_name=experiment_name,
        artifact_location=artifact_location,
    )
    with mlflow.start_run(run_name=run_name) as run:
        yield run


def log_parameters(run: Any, parameters: dict[str, Any]) -> None:
    if run is None:
        return
    import mlflow  # type: ignore

    mlflow.log_params({key: str(value) for key, value in parameters.items()})


def log_metrics(run: Any, metrics: dict[str, float]) -> None:
    if run is None:
        return
    import mlflow  # type: ignore

    mlflow.log_metrics({key: float(value) for key, value in metrics.items() if value is not None})


def log_artifact(run: Any, path: str | Path) -> None:
    if run is None:
        return
    import mlflow  # type: ignore

    mlflow.log_artifact(str(path))
