"""Evaluation visualizations for CO5/M5 evidence artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay


def _save(fig: Any, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return output


def plot_confusion(
    y_true: Any, predictions: Any, output_path: str | Path, title: str = "Confusion matrix"
) -> Path:
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_predictions(
        y_true, predictions, display_labels=["real", "fake"], ax=ax, cmap="Blues"
    )
    ax.set_title(title)
    return _save(fig, output_path)


def plot_roc_pr(
    y_true: Any, probabilities: Any, output_path: str | Path, label: str = "model"
) -> Path:
    positive = np.asarray(probabilities)[:, 1]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    RocCurveDisplay.from_predictions(y_true, positive, name=label, ax=axes[0])
    PrecisionRecallDisplay.from_predictions(y_true, positive, name=label, ax=axes[1])
    axes[0].set_title("ROC curve")
    axes[1].set_title("Precision-recall curve")
    return _save(fig, output_path)


def plot_reliability(
    y_true: Any, probabilities: Any, output_path: str | Path, n_bins: int = 10
) -> Path:
    positive = np.asarray(probabilities)[:, 1]
    observed, predicted = calibration_curve(y_true, positive, n_bins=n_bins, strategy="uniform")
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0, 1], [0, 1], "--", color="gray", label="perfect calibration")
    ax.plot(predicted, observed, marker="o", label="model")
    ax.set(
        xlabel="Mean predicted probability",
        ylabel="Fraction of positives",
        title="Reliability diagram",
    )
    ax.legend()
    return _save(fig, output_path)


def plot_learning_curve(
    train_sizes: Any, train_scores: Any, validation_scores: Any, output_path: str | Path
) -> Path:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(train_sizes, np.mean(train_scores, axis=1), label="training")
    ax.plot(train_sizes, np.mean(validation_scores, axis=1), label="validation")
    ax.fill_between(
        train_sizes, np.min(train_scores, axis=1), np.max(train_scores, axis=1), alpha=0.15
    )
    ax.set(xlabel="Training examples", ylabel="Score", title="Learning curve")
    ax.legend()
    return _save(fig, output_path)


def plot_validation_curve(
    parameter_values: Any,
    train_scores: Any,
    validation_scores: Any,
    output_path: str | Path,
    parameter_name: str = "parameter",
) -> Path:
    """Plot mean and spread of training/validation scores across a parameter grid."""
    values = np.asarray(parameter_values)
    train = np.asarray(train_scores)
    validation = np.asarray(validation_scores)
    if train.ndim == 1:
        train = train[:, None]
    if validation.ndim == 1:
        validation = validation[:, None]
    if len(values) != train.shape[0] or train.shape != validation.shape:
        raise ValueError("Validation-curve arrays have incompatible shapes")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(values, train.mean(axis=1), marker="o", label="training")
    ax.plot(values, validation.mean(axis=1), marker="o", label="validation")
    ax.fill_between(values, train.min(axis=1), train.max(axis=1), alpha=0.15)
    ax.fill_between(values, validation.min(axis=1), validation.max(axis=1), alpha=0.15)
    ax.set(xlabel=parameter_name, ylabel="Score", title="Validation curve")
    ax.legend()
    return _save(fig, output_path)


def plot_reliability_comparison(
    y_true: Any,
    probability_map: dict[str, Any],
    output_path: str | Path,
    n_bins: int = 10,
) -> Path:
    """Plot multiple calibration methods against the perfect-calibration diagonal."""
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0, 1], [0, 1], "--", color="gray", label="perfect calibration")
    for label, probabilities in probability_map.items():
        positive = np.asarray(probabilities)[:, 1]
        observed, predicted = calibration_curve(y_true, positive, n_bins=n_bins, strategy="uniform")
        ax.plot(predicted, observed, marker="o", label=label)
    ax.set(xlabel="Mean predicted probability", ylabel="Fraction of positives", title="Calibration comparison")
    ax.legend()
    return _save(fig, output_path)
