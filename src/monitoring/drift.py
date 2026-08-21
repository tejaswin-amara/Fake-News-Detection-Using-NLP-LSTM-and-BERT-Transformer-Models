"""Numerically stable data, probability, and text drift monitoring for CO6/M6.

Reference distributions must come from an approved training/reference window and
never from the final test set. References SRC-008, SRC-010, and SRC-029.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

FloatVector = NDArray[np.float64]
_MAX_DEFAULT_VALUES = 10_000
_EPSILON = 1e-12


def _finite_vector(values: Any, name: str, *, max_values: int = _MAX_DEFAULT_VALUES) -> tuple[FloatVector, int]:
    raw = np.asarray(values, dtype=np.float64).reshape(-1)
    if raw.size > max_values:
        raise ValueError(f"{name} exceeds the maximum of {max_values} values")
    finite = raw[np.isfinite(raw)]
    dropped = int(raw.size - finite.size)
    if finite.size < 2:
        raise ValueError(f"{name} requires at least two finite values")
    return finite, dropped


def _safe_edges(reference: FloatVector, current: FloatVector, bins: int) -> FloatVector:
    if bins < 2:
        raise ValueError("bins must be at least two")
    if np.all(reference == reference[0]) and np.all(current == reference[0]):
        if reference[0] == current[0]:
            return cast(FloatVector, np.asarray([reference[0] - 1.0, reference[0] + 1.0], dtype=np.float64))
        midpoint = float((reference[0] + current[0]) / 2.0)
        return cast(FloatVector, np.asarray([-np.inf, midpoint, np.inf], dtype=np.float64))
    if np.all(reference == reference[0]):
        low = min(float(reference[0]), float(np.min(current)))
        high = max(float(reference[0]), float(np.max(current)))
        if low == high:
            return cast(FloatVector, np.asarray([low - 1.0, high + 1.0], dtype=np.float64))
        return cast(FloatVector, np.asarray([-np.inf, low, high, np.inf], dtype=np.float64))
    quantiles = np.quantile(reference, np.linspace(0.0, 1.0, bins + 1))
    unique = np.unique(quantiles)
    if unique.size < 2:
        center = float(reference[0])
        spread = max(float(np.max(np.abs(current - center))), 1.0)
        unique = np.asarray([center - spread, center + spread], dtype=np.float64)
    edges = unique.astype(np.float64, copy=False)
    edges[0] = -np.inf
    edges[-1] = np.inf
    return cast(FloatVector, edges)


def ks_drift(reference: Any, current: Any, alpha: float = 0.05) -> dict[str, float | bool | int]:
    """Return a finite KS report, dropping non-finite generic monitoring values."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between zero and one")
    from scipy.stats import ks_2samp

    ref, ref_dropped = _finite_vector(reference, "reference")
    cur, cur_dropped = _finite_vector(current, "current")
    result = ks_2samp(ref, cur, alternative="two-sided", method="auto")
    statistic = float(result.statistic)
    p_value = float(result.pvalue)
    if not np.isfinite(statistic) or not np.isfinite(p_value):
        raise RuntimeError("KS calculation produced a non-finite result")
    return {
        "statistic": statistic,
        "p_value": p_value,
        "drift_detected": bool(p_value < alpha),
        "reference_n": int(ref.size),
        "current_n": int(cur.size),
        "reference_non_finite_dropped": ref_dropped,
        "current_non_finite_dropped": cur_dropped,
        "alpha": float(alpha),
    }


def population_stability_index(reference: Any, current: Any, bins: int = 10, epsilon: float = 1e-6) -> float:
    """Compute finite PSI with safe probabilities and explicit zero-variance handling."""
    if epsilon <= 0.0 or not np.isfinite(epsilon):
        raise ValueError("epsilon must be finite and positive")
    ref, _ = _finite_vector(reference, "reference")
    cur, _ = _finite_vector(current, "current")
    if np.all(ref == ref[0]) and np.all(cur == ref[0]):
        return 0.0
    edges = _safe_edges(ref, cur, bins)
    ref_counts, _ = np.histogram(ref, bins=edges)
    cur_counts, _ = np.histogram(cur, bins=edges)
    ref_total = max(int(ref_counts.sum()), 1)
    cur_total = max(int(cur_counts.sum()), 1)
    ref_pct = np.maximum(ref_counts.astype(np.float64) / ref_total, epsilon)
    cur_pct = np.maximum(cur_counts.astype(np.float64) / cur_total, epsilon)
    ref_pct /= ref_pct.sum()
    cur_pct /= cur_pct.sum()
    values = (cur_pct - ref_pct) * np.log(cur_pct / ref_pct)
    result = float(np.sum(values, dtype=np.float64))
    if not np.isfinite(result):
        raise RuntimeError("PSI calculation produced a non-finite result")
    return max(result, 0.0)


def _benjamini_hochberg(p_values: Sequence[float], alpha: float) -> tuple[list[float], list[bool]]:
    values = np.asarray(p_values, dtype=np.float64)
    if values.size == 0:
        return [], []
    order = np.argsort(values)
    adjusted = np.ones(values.size, dtype=np.float64)
    running = 1.0
    for rank in range(values.size - 1, -1, -1):
        index = int(order[rank])
        running = min(running, float(values[index]) * values.size / (rank + 1))
        adjusted[index] = min(max(running, 0.0), 1.0)
    return adjusted.tolist(), (adjusted <= alpha).tolist()


def monitor_features(
    reference: Mapping[str, Any],
    current: Mapping[str, Any],
    ks_alpha: float = 0.05,
    psi_threshold: float = 0.20,
) -> dict[str, Any]:
    if psi_threshold < 0.0 or not np.isfinite(psi_threshold):
        raise ValueError("psi_threshold must be finite and non-negative")
    names = sorted(set(reference).intersection(current))
    if not names:
        raise ValueError("No common feature names between reference and current data")
    raw_reports = {name: ks_drift(reference[name], current[name], alpha=ks_alpha) for name in names}
    adjusted_p, adjusted_flags = _benjamini_hochberg([float(raw_reports[name]["p_value"]) for name in names], ks_alpha)
    feature_reports: dict[str, Any] = {}
    for index, name in enumerate(names):
        ks = dict(raw_reports[name])
        ks["raw_drift_detected"] = ks["drift_detected"]
        ks["adjusted_p_value"] = adjusted_p[index]
        ks["drift_detected"] = adjusted_flags[index]
        psi = population_stability_index(reference[name], current[name])
        feature_reports[name] = {"ks": ks, "psi": psi, "psi_drift_detected": bool(psi >= psi_threshold)}
    return {
        "features": feature_reports,
        "multiple_testing": {"method": "benjamini_hochberg", "family_size": len(names), "alpha": ks_alpha},
        "thresholds": {"ks_alpha": ks_alpha, "psi": psi_threshold},
        "drift_detected": any(details["ks"]["drift_detected"] or details["psi_drift_detected"] for details in feature_reports.values()),
    }


def monitor_prediction_probabilities(
    reference: Any,
    current: Any,
    psi_threshold: float = 0.20,
    ks_alpha: float = 0.05,
) -> dict[str, Any]:
    ref = np.asarray(reference, dtype=np.float64).reshape(-1)
    cur = np.asarray(current, dtype=np.float64).reshape(-1)
    if not np.isfinite(ref).all() or not np.isfinite(cur).all():
        raise ValueError("Prediction probabilities must be finite")
    if np.any((ref < 0.0) | (ref > 1.0)) or np.any((cur < 0.0) | (cur > 1.0)):
        raise ValueError("Prediction probabilities must lie in [0, 1]")
    ref, _ = _finite_vector(ref, "reference_probabilities")
    cur, _ = _finite_vector(cur, "current_probabilities")
    psi = population_stability_index(ref, cur)
    ks = ks_drift(ref, cur, alpha=ks_alpha)
    detected = bool(psi >= psi_threshold or ks["drift_detected"])
    return {
        "psi": psi,
        "psi_threshold": psi_threshold,
        "psi_drift_detected": bool(psi >= psi_threshold),
        "ks": ks,
        "drift_detected": detected,
        "reference_n": int(ref.size),
        "current_n": int(cur.size),
    }


def _text_features(texts: Sequence[str], vocabulary: set[str] | None = None) -> dict[str, list[float]]:
    if any(not isinstance(text, str) for text in texts):
        raise ValueError("All monitored texts must be strings")
    token_lists = [re.findall(r"\b\w+\b", text.lower()) for text in texts]
    features: dict[str, list[float]] = {
        "character_length": [float(len(text)) for text in texts],
        "token_length": [float(len(tokens)) for tokens in token_lists],
        "sentence_length": [float(max(1, len(re.findall(r"[.!?]+", text)))) for text in texts],
        "lexical_diversity": [float(len(set(tokens)) / max(1, len(tokens))) for tokens in token_lists],
        "punctuation_ratio": [
            float(sum(not char.isalnum() and not char.isspace() for char in text) / max(1, len(text)))
            for text in texts
        ],
        "uppercase_ratio": [
            float(sum(char.isupper() for char in text) / max(1, len(text))) for text in texts
        ],
        "digit_ratio": [
            float(sum(char.isdigit() for char in text) / max(1, len(text))) for text in texts
        ],
    }
    if vocabulary is not None:
        features["oov_rate"] = [
            float(sum(token not in vocabulary for token in tokens) / max(1, len(tokens)))
            for tokens in token_lists
        ]
    return features


def monitor_text_batch(
    reference_texts: list[str],
    current_texts: list[str],
    oov_threshold: float = 0.20,
    length_threshold: float = 0.20,
    ks_alpha: float = 0.05,
) -> dict[str, Any]:
    if len(reference_texts) < 2 or len(current_texts) < 2:
        raise ValueError("Text drift requires at least two reference and current texts")
    if any(len(text) > 50_000 for text in [*reference_texts, *current_texts]):
        raise ValueError("Monitored text exceeds the maximum length")
    reference_vocab = {
        token for text in reference_texts for token in re.findall(r"\b\w+\b", text.lower())
    }
    reference = _text_features(reference_texts, reference_vocab)
    current = _text_features(current_texts, reference_vocab)
    names = sorted(reference)
    raw_reports = {name: ks_drift(reference[name], current[name], alpha=ks_alpha) for name in names}
    adjusted_p, adjusted_flags = _benjamini_hochberg([float(raw_reports[name]["p_value"]) for name in names], ks_alpha)
    feature_reports: dict[str, Any] = {}
    drifted_features: list[str] = []
    for index, name in enumerate(names):
        ks = dict(raw_reports[name])
        ks["raw_drift_detected"] = ks["drift_detected"]
        ks["adjusted_p_value"] = adjusted_p[index]
        ks["drift_detected"] = adjusted_flags[index]
        reference_mean = float(np.mean(reference[name], dtype=np.float64))
        current_mean = float(np.mean(current[name], dtype=np.float64))
        difference = abs(current_mean - reference_mean)
        relative_shift = min(difference / max(abs(reference_mean), _EPSILON), 1e12)
        threshold = oov_threshold if name == "oov_rate" else length_threshold
        detected = bool(ks["drift_detected"] or relative_shift >= threshold)
        feature_reports[name] = {
            "ks": ks,
            "reference_mean": reference_mean,
            "current_mean": current_mean,
            "relative_shift": relative_shift,
            "threshold": threshold,
            "drift_detected": detected,
        }
        if detected:
            drifted_features.append(name)
    return {
        "features": feature_reports,
        "drifted_features": drifted_features,
        "multiple_testing": {"method": "benjamini_hochberg", "family_size": len(names), "alpha": ks_alpha},
        "thresholds": {
            "oov_rate": oov_threshold,
            "length_shift": length_threshold,
            "ks_alpha": ks_alpha,
        },
        "drift_detected": bool(drifted_features),
        "reference_n": len(reference_texts),
        "current_n": len(current_texts),
    }


def build_retraining_signal(
    report: Mapping[str, Any],
    baseline_revision: str,
    window_id: str,
    cooldown_hours: int = 24,
) -> dict[str, Any]:
    if cooldown_hours < 0:
        raise ValueError("cooldown_hours must be non-negative")
    raw_drifted = report.get("drifted_features", [])
    if not isinstance(raw_drifted, Sequence) or isinstance(raw_drifted, str | bytes):
        raise ValueError("drifted_features must be a sequence")
    drifted = sorted({str(item) for item in raw_drifted})
    triggered = bool(report.get("drift_detected", False))
    return {
        "triggered": triggered,
        "reason": ";".join(drifted) if drifted else "no_drift",
        "drifted_features": drifted,
        "baseline_revision": str(baseline_revision),
        "window_id": str(window_id),
        "suggested_action": "review_and_retrain" if triggered else "continue_monitoring",
        "requires_human_approval": True,
        "cooldown_hours": cooldown_hours,
        "cooldown_key": f"{baseline_revision}:{window_id}:{','.join(drifted)}",
        "generated_at": datetime.now(UTC).isoformat(),
        "side_effects": "none",
    }


def save_report(report: Mapping[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dict(report), indent=2, allow_nan=False, default=float), encoding="utf-8")
