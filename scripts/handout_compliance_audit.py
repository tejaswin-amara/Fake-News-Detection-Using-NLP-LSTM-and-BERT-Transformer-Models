#!/usr/bin/env python3
"""Executable compliance gate for the 25SC2107E handout.

The gate checks that the repository contains the implementation/documentation
surfaces needed by M1-M6. It intentionally does not claim that full-data model
training happened; execution evidence is generated separately by the pipeline.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class Requirement:
    module: str
    outcome: str
    topic: str
    paths: tuple[str, ...]


REQUIREMENTS: tuple[Requirement, ...] = (
    Requirement("M1", "CO1", "end-to-end lifecycle", ("src/data", "src/features", "src/models", "src/evaluation", "src/serving", "src/monitoring")),
    Requirement("M2", "CO2", "linear regression", ("src/models/handout_models.py",)),
    Requirement("M2", "CO2", "ridge/lasso/elastic-net/logistic/multinomial logistic", ("src/models/classical.py", "src/models/handout_models.py")),
    Requirement("M2", "CO2", "scaling, encoding, missing values", ("src/features/preprocessing.py",)),
    Requirement("M3", "CO3", "decision trees, pruning, random forest/OOB", ("src/models/classical.py",)),
    Requirement("M3", "CO3", "AdaBoost, XGBoost, LightGBM", ("src/models/handout_models.py", "src/models/classical.py")),
    Requirement("M3", "CO3", "feature importance and SHAP", ("src/models/classical.py",)),
    Requirement("M4", "CO4", "k-means, mini-batch, hierarchical, DBSCAN", ("src/models/unsupervised.py",)),
    Requirement("M4", "CO4", "PCA, t-SNE, UMAP", ("src/models/unsupervised.py",)),
    Requirement("M4", "CO4", "anomaly detection", ("src/models/unsupervised.py", "src/models/handout_models.py")),
    Requirement("M5", "CO5", "train/validation/test and stratified/nested CV", ("src/evaluation/metrics.py",)),
    Requirement("M5", "CO5", "classification and regression metrics", ("src/evaluation/metrics.py",)),
    Requirement("M5", "CO5", "calibration and reliability", ("src/evaluation/metrics.py", "src/evaluation/plots.py")),
    Requirement("M5", "CO5", "grid/random/Bayesian search", ("src/evaluation/search.py",)),
    Requirement("M5", "CO5", "statistical comparison", ("src/evaluation/metrics.py",)),
    Requirement("M6", "CO6", "training-serving skew boundary", ("src/serving/predictor.py",)),
    Requirement("M6", "CO6", "ONNX/native packaging", ("src/serving/export.py",)),
    Requirement("M6", "CO6", "REST serving", ("src/serving/app.py",)),
    Requirement("M6", "CO6", "monitoring and retraining signals", ("src/monitoring/drift.py",)),
    Requirement("M6", "CO6", "MLflow and DVC", ("src/tracking.py", "dvc.yaml",)),
    Requirement("M1-M6", "CO1-CO6", "source and resource governance", ("docs/sources.md", "docs/HANDOUT_RESOURCE_MATRIX.md", "docs/RESOURCE_UTILIZATION_AND_APPLICABILITY.md")),
)


def audit(root: Path) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    failures = 0
    for requirement in REQUIREMENTS:
        present = [path for path in requirement.paths if (root / path).exists()]
        missing = [path for path in requirement.paths if not (root / path).exists()]
        # A requirement is satisfied when at least one declared implementation
        # surface exists. Some topics intentionally share one implementation.
        ok = bool(present)
        if not ok:
            failures += 1
        rows.append({**asdict(requirement), "present": present, "missing": missing, "status": "PASS" if ok else "FAIL"})
    return {
        "handout": "Machine Learning 25SC2107E",
        "modules": ["M1", "M2", "M3", "M4", "M5", "M6"],
        "requirements": rows,
        "pass_count": len(REQUIREMENTS) - failures,
        "fail_count": failures,
        "implementation_gate_passed": failures == 0,
        "metrics_execution_note": "This gate verifies implementation surfaces only; it does not fabricate or infer full-data experimental results.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = audit(args.root.resolve())
    payload = json.dumps(result, indent=2)
    print(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    return 0 if result["implementation_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
