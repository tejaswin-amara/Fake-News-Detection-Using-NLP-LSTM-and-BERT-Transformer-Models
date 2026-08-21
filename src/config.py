"""Configuration, reproducibility, and structured logging helpers."""

from __future__ import annotations

import contextvars
import logging
import os
import sys
from collections.abc import MutableMapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog
import yaml

_REQUEST_ID = contextvars.ContextVar("fake_news_request_id", default="system")
_JSON_HANDLER_MARKER = "_fake_news_json_handler"


def current_request_id() -> str:
    """Return the bounded request identifier for the current execution context."""
    return _REQUEST_ID.get()


def bind_request_id(request_id: str) -> contextvars.Token[str]:
    """Bind a request identifier to the current async/thread context."""
    token = _REQUEST_ID.set(request_id)
    structlog.contextvars.bind_contextvars(request_id=request_id)
    return token


def reset_request_id(token: contextvars.Token[str]) -> None:
    """Restore the previous request context and remove structlog request binding."""
    _REQUEST_ID.reset(token)
    structlog.contextvars.unbind_contextvars("request_id")


def _request_id_processor(
    _logger: Any,
    _method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    event_dict.setdefault("request_id", current_request_id())
    return event_dict


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = current_request_id()
        return True


def configure_logging(level: str | None = None) -> None:
    """Configure one idempotent JSON logging pipeline for app and server loggers."""
    configured_name = level if level is not None else os.getenv("LOG_LEVEL", "INFO")
    configured_level = configured_name.upper()
    numeric_level = getattr(logging, configured_level, logging.INFO)
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
        _request_id_processor,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        if getattr(handler, _JSON_HANDLER_MARKER, False):
            root_logger.removeHandler(handler)
    handler = logging.StreamHandler(sys.stdout)
    setattr(handler, _JSON_HANDLER_MARKER, True)
    handler.addFilter(_RequestIdFilter())
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(numeric_level)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "src"):
        named_logger = logging.getLogger(logger_name)
        named_logger.handlers.clear()
        named_logger.propagate = True
        named_logger.setLevel(numeric_level)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            _request_id_processor,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )


@dataclass(frozen=True)
class ProjectConfig:
    """Small typed view over the YAML configuration."""

    root: Path
    values: dict[str, Any]

    @property
    def seed(self) -> int:
        return int(self.values.get("project", {}).get("random_seed", 42))

    @property
    def paths(self) -> dict[str, Path]:
        raw = self.values.get("paths", {})
        return {key: self.root / value for key, value in raw.items() if isinstance(value, str)}


def load_config(
    path: str | Path = "configs/default.yaml", root: str | Path | None = None
) -> ProjectConfig:
    config_path = Path(path).resolve()
    project_root = Path(root).resolve() if root else config_path.parent.parent
    with config_path.open("r", encoding="utf-8") as handle:
        values = yaml.safe_load(handle) or {}
    return ProjectConfig(root=project_root, values=values)


def ensure_directories(config: ProjectConfig) -> None:
    for directory in config.paths.values():
        directory.mkdir(parents=True, exist_ok=True)
