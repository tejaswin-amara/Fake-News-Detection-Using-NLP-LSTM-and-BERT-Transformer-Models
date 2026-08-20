"""Audit source-register coverage for tracked external references."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

URL_RE = re.compile(r"https?://[^\s)\]>\"']+")
SOURCE_ID_RE = re.compile(r"SRC-\d{3}")
IGNORED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".toml", ".txt", ".json", ".ipynb"}
RESERVED_FIXTURE_URLS = {"https://example.com"}
LOCAL_OPERATIONAL_URL_RE = re.compile(r"https?://(?:localhost|127\.0\.0\.1|api)(?::\d+)?(?:/|$)")


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


def audit(root: Path) -> tuple[list[str], list[str]]:
    source_register = (root / "docs" / "sources.md").read_text(encoding="utf-8")
    source_yaml = (root / "docs" / "sources.yaml").read_text(encoding="utf-8")
    combined_register = source_register + "\n" + source_yaml
    source_ids = set(SOURCE_ID_RE.findall(combined_register))
    missing_urls: list[str] = []
    missing_ids: list[str] = []
    for path in iter_text_files(root):
        if path.name in {"sources.md", "sources.yaml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for url in URL_RE.findall(text):
            normalized = url.rstrip(".,;:")
            if (
                LOCAL_OPERATIONAL_URL_RE.match(normalized) is None
                and normalized not in combined_register
                and normalized not in RESERVED_FIXTURE_URLS
                and normalized
                not in {
                    "https://github.com/tejaswin-amara/Fake-News-Detection-Using-NLP-LSTM-and-BERT-Transformer-Models"
                }
            ):
                missing_urls.append(f"{path.relative_to(root)}: {normalized}")
        for source_id in SOURCE_ID_RE.findall(text):
            if source_id not in source_ids:
                missing_ids.append(f"{path.relative_to(root)}: {source_id}")
    return sorted(set(missing_urls)), sorted(set(missing_ids))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    missing_urls, missing_ids = audit(Path(args.root).resolve())
    if missing_urls or missing_ids:
        if missing_urls:
            print("Unregistered URLs:")
            print("\n".join(missing_urls))
        if missing_ids:
            print("Unknown source identifiers:")
            print("\n".join(missing_ids))
        return 1
    print("Source audit passed: all discovered URLs and source identifiers are registered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
