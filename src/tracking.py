"""Optional MLflow experiment-tracking integration.

References SRC-033 in docs/sources.md. Tracking is disabled by default so the
classical/API paths remain usable without a tracking server.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any


@contextmanager
def experiment_run(
    enabled: bool = False,
    tracking_uri: str = "mlruns",
    experiment_name: str = "fake-news-detection",
    run_name: str | None = None,
) -> Iterator[Any]:
    if not enabled:
        yield None
        return
    try:
        import mlflow  # type: ignore
    except ImportError as exc:
        raise RuntimeError("MLflow tracking was enabled but mlflow is not installed") from exc
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
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
