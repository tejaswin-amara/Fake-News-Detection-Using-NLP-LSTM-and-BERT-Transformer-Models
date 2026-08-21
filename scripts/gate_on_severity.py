"""Gate machine-readable dependency findings by explicit severity.

pip-audit JSON versions differ in whether advisory severity is included. This
script fails explicit high/critical findings and reports unrated findings for
manual triage instead of inventing severity metadata.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _severity_values(vulnerability: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    raw = vulnerability.get("severity")
    if isinstance(raw, str):
        values.add(raw.lower())
    elif isinstance(raw, list):
        values.update(str(value).lower() for value in raw)
    ratings = vulnerability.get("ratings")
    if isinstance(ratings, list):
        for rating in ratings:
            if isinstance(rating, dict) and rating.get("severity"):
                values.add(str(rating["severity"]).lower())
    return values


def gate(report: dict[str, Any], max_severity: str = "high") -> tuple[int, dict[str, Any]]:
    threshold = {"low": 1, "medium": 2, "high": 3, "critical": 4}[max_severity]
    blocked: list[dict[str, Any]] = []
    unrated: list[dict[str, Any]] = []
    dependencies = report.get("dependencies", [])
    if not isinstance(dependencies, list):
        raise ValueError("pip-audit report must contain a dependencies list")
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            continue
        name = str(dependency.get("name", "unknown"))
        version = str(dependency.get("version", "unknown"))
        vulnerabilities = dependency.get("vulns", dependency.get("vulnerabilities", []))
        if not isinstance(vulnerabilities, list):
            continue
        for vulnerability in vulnerabilities:
            if not isinstance(vulnerability, dict):
                continue
            severities = _severity_values(vulnerability)
            advisory = {"name": name, "version": version, "id": vulnerability.get("id"), "severity": sorted(severities)}
            if not severities:
                unrated.append(advisory)
                continue
            numeric = max(({"low": 1, "moderate": 2, "medium": 2, "high": 3, "critical": 4}.get(value, 0) for value in severities), default=0)
            if numeric >= threshold:
                blocked.append(advisory)
    result = {"blocked": blocked, "unrated": unrated, "blocked_count": len(blocked), "unrated_count": len(unrated), "max_severity": max_severity}
    return (1 if blocked else 0), result


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate pip-audit JSON by explicit severity")
    parser.add_argument("--report", required=True)
    parser.add_argument("--max-severity", choices=["low", "medium", "high", "critical"], default="high")
    args = parser.parse_args()
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    status, result = gate(report, args.max_severity)
    print(json.dumps(result, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
