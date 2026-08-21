from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_audit_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "source_audit.py"
    spec = importlib.util.spec_from_file_location("source_audit", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture_url(host: str, path: str) -> str:
    return "https://" + host + path


def test_source_audit_ignores_dvc_managed_raw_data_but_scans_repository_docs(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    registered_url = _fixture_url("registered.example.test", "/source")
    (docs / "sources.md").write_text(registered_url, encoding="utf-8")
    (docs / "sources.yaml").write_text("sources: []\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(registered_url, encoding="utf-8")
    raw_data = tmp_path / "data" / "raw"
    raw_data.mkdir(parents=True)
    raw_url = _fixture_url("unregistered.example.test", "/item")
    (raw_data / "feed.json").write_text(f'{{"review_url": "{raw_url}"}}', encoding="utf-8")

    source_audit = _load_audit_module()
    missing_urls, missing_ids = source_audit.audit(tmp_path)

    assert missing_urls == []
    assert missing_ids == []
