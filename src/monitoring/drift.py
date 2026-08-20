"""Feature and embedding drift monitoring using KS and PSI.

Compliant with M6/CO6. References SRC-008, SRC-010, and SRC-029 in
`docs/sources.md`. Reference distributions must be created from an approved
training/reference window and never from the final test set.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


def ks_drift(reference: Any, current: Any, alpha: float = 0.05) -> dict[str, float | bool]:
    from scipy.stats import ks_2samp  # type: ignore

    ref = np.asarray(reference, dtype=float)
    cur = np.asarray(current, dtype=float)
    ref = ref[np.isfinite(ref)]
    cur = cur[np.isfinite(cur)]
    if len(ref) < 2 or len(cur) < 2:
        raise ValueError("KS test requires at least two finite values in each sample")
    result = ks_2samp(ref, cur, alternative="two-sided", method="auto")
    return {
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue),
        "drift_detected": bool(result.pvalue < alpha),
    }


def population_stability_index(
    reference: Any, current: Any, bins: int = 10, epsilon: float = 1e-6
) -> float:
    ref = np.asarray(reference, dtype=float)
    cur = np.asarray(current, dtype=float)
    ref = ref[np.isfinite(ref)]
    cur = cur[np.isfinite(cur)]
    if len(ref) < 2 or len(cur) < 2:
        raise ValueError("PSI requires at least two finite values in each sample")
    edges = np.unique(np.quantile(ref, np.linspace(0.0, 1.0, bins + 1)))
    if len(edges) < 3:
        low, high = float(ref.min()), float(ref.max())
        if low == high:
            return 0.0
        edges = np.linspace(low, high, bins + 1)
    ref_counts, _ = np.histogram(ref, bins=edges)
    cur_counts, _ = np.histogram(cur, bins=edges)
    ref_pct = np.maximum(ref_counts / max(1, ref_counts.sum()), epsilon)
    cur_pct = np.maximum(cur_counts / max(1, cur_counts.sum()), epsilon)
    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


def monitor_features(
    reference: dict[str, Any],
    current: dict[str, Any],
    ks_alpha: float = 0.05,
    psi_threshold: float = 0.20,
) -> dict[str, Any]:
    names = sorted(set(reference).intersection(current))
    if not names:
        raise ValueError("No common feature names between reference and current data")
    report: dict[str, Any] = {
        "features": {},
        "thresholds": {"ks_alpha": ks_alpha, "psi": psi_threshold},
    }
    for name in names:
        ks = ks_drift(reference[name], current[name], alpha=ks_alpha)
        psi = population_stability_index(reference[name], current[name])
        report["features"][name] = {
            "ks": ks,
            "psi": psi,
            "psi_drift_detected": psi >= psi_threshold,
        }
    report["drift_detected"] = any(
        details["ks"]["drift_detected"] or details["psi_drift_detected"]
        for details in report["features"].values()
    )
    return report


def save_report(report: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, default=float), encoding="utf-8")
