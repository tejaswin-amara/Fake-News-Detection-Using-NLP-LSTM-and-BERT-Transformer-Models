"""Resilient MLflow experiment-tracking integration.

References SRC-033 and SRC-036 in docs/sources.md. Tracking is disabled by
default; transient remote failures retry and may fall back to an explicit local
file store without silently discarding a requested run.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

LOGGER = logging.getLogger(__name__)


def _local_uri(value: str | Path) -> str:
    """Convert a local path to a stable MLflow file URI and create it."""
    candidate = str(value)
    parsed = urlparse(candidate)
    if parsed.scheme:
        return candidate
    path = Path(candidate).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path.as_uri()


def _initialize_tracking_once(
    tracking_uri: str,
    experiment_name: str,
    artifact_location: str | None,
) -> dict[str, str]:
    import mlflow

    resolved_uri = _local_uri(tracking_uri)
    resolved_artifacts = _local_uri(artifact_location) if artifact_location else None
    mlflow.set_tracking_uri(resolved_uri)
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name, artifact_location=resolved_artifacts)
        experiment = mlflow.get_experiment(experiment_id)
    if experiment is None:
        raise RuntimeError(f"MLflow experiment initialization returned no experiment: {experiment_name}")
    mlflow.set_experiment(experiment_name)
    return {
        "tracking_uri": resolved_uri,
        "experiment_name": experiment.name,
        "experiment_id": experiment.experiment_id,
        "artifact_location": str(experiment.artifact_location),
    }


def initialize_tracking(
    tracking_uri: str = "mlruns",
    experiment_name: str = "fake-news-detection",
    artifact_location: str | None = None,
    retry_attempts: int = 3,
    retry_backoff_seconds: float = 0.5,
    local_fallback_uri: str | None = None,
    fail_on_remote_error: bool = False,
) -> dict[str, str]:
    """Initialize MLflow with bounded retry and an explicit local fallback."""
    if retry_attempts < 1 or retry_backoff_seconds < 0.0:
        raise ValueError("retry_attempts must be positive and retry_backoff_seconds non-negative")
    candidates = [tracking_uri]
    if local_fallback_uri and local_fallback_uri not in candidates:
        candidates.append(local_fallback_uri)
    last_error: Exception | None = None
    for candidate_index, candidate in enumerate(candidates):
        for attempt in range(retry_attempts):
            try:
                result = _initialize_tracking_once(candidate, experiment_name, artifact_location)
                if candidate_index > 0:
                    result["fallback_used"] = "true"
                return result
            except Exception as exc:
                last_error = exc
                if attempt + 1 < retry_attempts:
                    time.sleep(retry_backoff_seconds * (2**attempt))
        if candidate_index == 0 and len(candidates) > 1:
            LOGGER.warning("MLflow primary tracking failed; trying configured local fallback")
    if last_error is None:
        raise RuntimeError("MLflow tracking initialization failed without an exception")
    if fail_on_remote_error or len(candidates) == 1:
        raise RuntimeError(f"MLflow tracking initialization failed: {type(last_error).__name__}") from last_error
    raise RuntimeError(f"MLflow local fallback failed: {type(last_error).__name__}") from last_error


@contextmanager
def experiment_run(
    enabled: bool = False,
    tracking_uri: str = "mlruns",
    experiment_name: str = "fake-news-detection",
    run_name: str | None = None,
    artifact_location: str | None = None,
    retry_attempts: int = 3,
    retry_backoff_seconds: float = 0.5,
    local_fallback_uri: str | None = None,
    fail_on_remote_error: bool = False,
) -> Iterator[Any]:
    if not enabled:
        yield None
        return
    import mlflow

    initialize_tracking(
        tracking_uri=tracking_uri,
        experiment_name=experiment_name,
        artifact_location=artifact_location,
        retry_attempts=retry_attempts,
        retry_backoff_seconds=retry_backoff_seconds,
        local_fallback_uri=local_fallback_uri,
        fail_on_remote_error=fail_on_remote_error,
    )
    with mlflow.start_run(run_name=run_name) as run:
        yield run


def log_parameters(run: Any, parameters: dict[str, Any]) -> None:
    if run is None:
        return
    import mlflow

    try:
        mlflow.log_params({key: str(value) for key, value in parameters.items()})
    except Exception as exc:
        LOGGER.warning("MLflow parameter logging failed: %s", type(exc).__name__)


def log_metrics(run: Any, metrics: dict[str, float]) -> None:
    if run is None:
        return
    import mlflow

    try:
        mlflow.log_metrics({key: float(value) for key, value in metrics.items() if value is not None})
    except Exception as exc:
        LOGGER.warning("MLflow metric logging failed: %s", type(exc).__name__)


def log_artifact(run: Any, path: str | Path) -> None:
    if run is None:
        return
    import mlflow

    try:
        mlflow.log_artifact(str(path))
    except Exception as exc:
        LOGGER.warning("MLflow artifact logging failed for %s: %s", Path(path).name, type(exc).__name__)
