"""Data, prediction-probability, and text-domain drift monitoring for CO6/M6.

Reference distributions must come from an approved training/reference window and
never from the final test set. References SRC-008, SRC-010, and SRC-029.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np


def ks_drift(reference: Any, current: Any, alpha: float = 0.05) -> dict[str, float | bool | int]:
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
        "reference_n": int(len(ref)),
        "current_n": int(len(cur)),
        "alpha": float(alpha),
    }


def population_stability_index(reference: Any, current: Any, bins: int = 10, epsilon: float = 1e-6) -> float:
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


def monitor_features(reference: dict[str, Any], current: dict[str, Any], ks_alpha: float = 0.05, psi_threshold: float = 0.20) -> dict[str, Any]:
    names = sorted(set(reference).intersection(current))
    if not names:
        raise ValueError("No common feature names between reference and current data")
    report: dict[str, Any] = {"features": {}, "thresholds": {"ks_alpha": ks_alpha, "psi": psi_threshold}}
    for name in names:
        ks = ks_drift(reference[name], current[name], alpha=ks_alpha)
        psi = population_stability_index(reference[name], current[name])
        report["features"][name] = {"ks": ks, "psi": psi, "psi_drift_detected": psi >= psi_threshold}
    report["drift_detected"] = any(details["ks"]["drift_detected"] or details["psi_drift_detected"] for details in report["features"].values())
    return report


def monitor_prediction_probabilities(reference: Any, current: Any, psi_threshold: float = 0.20, ks_alpha: float = 0.05) -> dict[str, Any]:
    ref = np.asarray(reference, dtype=float)
    cur = np.asarray(current, dtype=float)
    if np.any((ref < 0) | (ref > 1)) or np.any((cur < 0) | (cur > 1)):
        raise ValueError("Prediction probabilities must lie in [0, 1]")
    psi = population_stability_index(ref, cur)
    ks = ks_drift(ref, cur, alpha=ks_alpha)
    return {"psi": psi, "psi_threshold": psi_threshold, "psi_drift_detected": psi >= psi_threshold, "ks": ks, "drift_detected": bool(psi >= psi_threshold or ks["drift_detected"]), "reference_n": len(ref), "current_n": len(cur)}


def _text_features(texts: list[str], vocabulary: set[str] | None = None) -> dict[str, list[float]]:
    token_lists = [re.findall(r"\b\w+\b", text.lower()) for text in texts]
    features: dict[str, list[float]] = {
        "character_length": [float(len(text)) for text in texts],
        "token_length": [float(len(tokens)) for tokens in token_lists],
        "sentence_length": [float(max(1, len(re.findall(r"[.!?]+", text)))) for text in texts],
        "lexical_diversity": [float(len(set(tokens)) / max(1, len(tokens))) for tokens in token_lists],
        "punctuation_ratio": [float(sum(not char.isalnum() and not char.isspace() for char in text) / max(1, len(text))) for text in texts],
        "uppercase_ratio": [float(sum(char.isupper() for char in text) / max(1, len(text))) for text in texts],
        "digit_ratio": [float(sum(char.isdigit() for char in text) / max(1, len(text))) for text in texts],
    }
    if vocabulary is not None:
        features["oov_rate"] = [float(sum(token not in vocabulary for token in tokens) / max(1, len(tokens))) for tokens in token_lists]
    return features


def monitor_text_batch(reference_texts: list[str], current_texts: list[str], oov_threshold: float = 0.20, length_threshold: float = 0.20, ks_alpha: float = 0.05) -> dict[str, Any]:
    if len(reference_texts) < 2 or len(current_texts) < 2:
        raise ValueError("Text drift requires at least two reference and current texts")
    reference_vocab = set(token for text in reference_texts for token in re.findall(r"\b\w+\b", text.lower()))
    reference = _text_features(reference_texts, reference_vocab)
    current = _text_features(current_texts, reference_vocab)
    feature_reports: dict[str, Any] = {}
    drifted_features: list[str] = []
    for name in sorted(reference):
        ks = ks_drift(reference[name], current[name], alpha=ks_alpha)
        reference_mean = float(np.mean(reference[name]))
        current_mean = float(np.mean(current[name]))
        relative_shift = abs(current_mean - reference_mean) / max(abs(reference_mean), 1e-12)
        threshold = oov_threshold if name == "oov_rate" else length_threshold if name in {"character_length", "token_length", "sentence_length"} else length_threshold
        detected = bool(ks["drift_detected"] or relative_shift >= threshold)
        feature_reports[name] = {"ks": ks, "reference_mean": reference_mean, "current_mean": current_mean, "relative_shift": relative_shift, "threshold": threshold, "drift_detected": detected}
        if detected:
            drifted_features.append(name)
    return {"features": feature_reports, "drifted_features": drifted_features, "thresholds": {"oov_rate": oov_threshold, "length_shift": length_threshold, "ks_alpha": ks_alpha}, "drift_detected": bool(drifted_features), "reference_n": len(reference_texts), "current_n": len(current_texts)}


def build_retraining_signal(report: dict[str, Any], baseline_revision: str, window_id: str, cooldown_hours: int = 24) -> dict[str, Any]:
    drifted = report.get("drifted_features", [])
    triggered = bool(report.get("drift_detected", False))
    return {
        "triggered": triggered,
        "reason": ";".join(drifted) if drifted else "no_drift",
        "drifted_features": drifted,
        "baseline_revision": baseline_revision,
        "window_id": window_id,
        "suggested_action": "review_and_retrain" if triggered else "continue_monitoring",
        "requires_human_approval": True,
        "cooldown_hours": cooldown_hours,
        "cooldown_key": f"{baseline_revision}:{window_id}:{','.join(drifted)}",
        "generated_at": datetime.now(UTC).isoformat(),
        "side_effects": "none",
    }


def save_report(report: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, default=float), encoding="utf-8")
