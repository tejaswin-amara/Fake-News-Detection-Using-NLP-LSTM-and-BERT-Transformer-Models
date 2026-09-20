"""Pydantic V2 Schemas for inference requests, token attributions, and benchmarks.

Matches frontend TypeScript contracts defined in `frontend/src/types/inference.ts`.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TextClassificationRequest(BaseModel):
    """Payload for text classification requests."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=100_000,
        description="Input text sequence to evaluate for veracity.",
        examples=["Central Banks coordinate liquidity backstop in joint statement."],
    )
    title: str = Field(
        default="",
        max_length=5_000,
        description="Optional headline or article title.",
        examples=["Global Economic Update"],
    )
    model: Literal["lstm", "bert", "both"] | None = Field(
        default="both",
        description="Target neural architecture for inference: lstm, bert, or both.",
    )


class TokenAttribution(BaseModel):
    """Token-level saliency attribution data for explainability visualization."""

    id: str = Field(..., description="Unique token instance identifier.")
    token: str = Field(..., description="Token text segment.")
    weight: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized attribution saliency weight [0.0 - 1.0].",
    )
    direction: Literal["real", "fake", "neutral"] = Field(
        ...,
        description="Directional impact of this token toward real, fake, or neutral veracity.",
    )
    rawScore: float | None = Field(
        default=None,
        description="Raw unnormalized logit/gradient attribution score.",
    )
    reason: str | None = Field(
        default=None,
        description="Explainability rationale for this token attribution.",
    )


class InferenceResponse(BaseModel):
    """Inference result for a single neural model architecture."""

    modelId: Literal["lstm", "bert"] = Field(..., description="Model identifier: lstm or bert.")
    modelName: str = Field(..., description="Human-readable descriptive model name.")
    verdict: Literal["REAL", "FAKE", "UNCERTAIN"] = Field(
        ...,
        description="Calibrated veracity verdict: REAL, FAKE, or UNCERTAIN.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Winning class confidence probability [0.0 - 1.0].",
    )
    probabilityFake: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Calibrated probability of fake content [0.0 - 1.0].",
    )
    probabilityReal: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Calibrated probability of real content [0.0 - 1.0].",
    )
    latencyMs: float = Field(
        ...,
        ge=0.0,
        description="Model inference execution latency in milliseconds.",
    )
    tokensCount: int = Field(
        ...,
        ge=0,
        description="Number of tokens processed by the model tokenizer.",
    )
    paramCount: str = Field(
        ...,
        description="Parameter count description (e.g. ~4.2M params).",
    )
    architecture: str = Field(
        ...,
        description="Summary of the model architecture and layers.",
    )
    saliencyTokens: list[TokenAttribution] = Field(
        default_factory=list,
        description="Token-level attribution heatmap items.",
    )


class ComparisonResponse(BaseModel):
    """Dual-model comparison inference response."""

    id: str = Field(..., description="Unique inference request ID.")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of the inference execution.")
    title: str = Field(default="", description="Evaluated article title.")
    text: str = Field(..., description="Evaluated article body text.")
    targetModel: Literal["lstm", "bert", "both"] = Field(
        ...,
        description="Target model(s) requested for this analysis.",
    )
    lstm: InferenceResponse | None = Field(
        default=None,
        description="Bi-LSTM inference result if requested.",
    )
    bert: InferenceResponse | None = Field(
        default=None,
        description="BERT inference result if requested.",
    )
    consensus: Literal["AGREEMENT", "DIVERGENCE"] | None = Field(
        default=None,
        description="Consensus between models when both are evaluated.",
    )
    differentialConfidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Absolute difference between model confidence scores.",
    )
    isSimulated: bool = Field(
        default=False,
        description="Whether fallback simulation heuristics were used.",
    )
    simulationNotice: str | None = Field(
        default=None,
        description="Simulation or fallback notice explaining offline execution mode.",
    )


class ConfusionMatrixSchema(BaseModel):
    """2x2 empirical confusion matrix."""

    tp: int = Field(..., ge=0, description="True Positives (Deceptive correctly identified).")
    fp: int = Field(..., ge=0, description="False Positives (Credible falsely flagged).")
    tn: int = Field(..., ge=0, description="True Negatives (Credible correctly identified).")
    fn: int = Field(..., ge=0, description="False Negatives (Deceptive missed).")


class RocCurvePointSchema(BaseModel):
    """Single point along empirical ROC curve."""

    fpr: float = Field(..., ge=0.0, le=1.0, description="False Positive Rate.")
    tpr: float = Field(..., ge=0.0, le=1.0, description="True Positive Rate.")


class BenchmarkMetricsResponse(BaseModel):
    """Empirical benchmark evaluation metrics for a model architecture."""

    name: str = Field(..., description="Model identifier name.")
    family: str = Field(..., description="Architectural family.")
    tag: str = Field(..., description="Descriptive tag or award.")
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Classification accuracy.")
    precision: float = Field(..., ge=0.0, le=1.0, description="Positive predictive value.")
    recall: float = Field(..., ge=0.0, le=1.0, description="True positive rate.")
    f1Score: float = Field(
        ..., ge=0.0, le=1.0, description="Harmonic mean of precision and recall."
    )
    rocAuc: float = Field(..., ge=0.0, le=1.0, description="Area under ROC curve.")
    brierScore: float = Field(..., ge=0.0, le=1.0, description="Brier calibration score.")
    latencyMs: float = Field(..., ge=0.0, description="P95 inference latency in milliseconds.")
    modelSizeMb: float = Field(..., ge=0.0, description="Serialized model footprint in megabytes.")
    paramCount: str = Field(..., description="Total parameter count string.")
    ramMb: int = Field(..., ge=0, description="Working RAM footprint in megabytes.")
    interpretability: str = Field(..., description="Explainability mechanism.")
    operationalRisk: str = Field(..., description="Production operational risk assessment.")
    isChampion: bool = Field(
        default=False, description="Whether this model is designated production champion."
    )
    confusionMatrix: ConfusionMatrixSchema = Field(
        ..., description="Empirical 2x2 confusion matrix."
    )
    rocCurve: list[RocCurvePointSchema] = Field(
        default_factory=list, description="Empirical ROC curve coordinates."
    )
