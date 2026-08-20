"""Configuration and reproducibility helpers for the fake-news project."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


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
