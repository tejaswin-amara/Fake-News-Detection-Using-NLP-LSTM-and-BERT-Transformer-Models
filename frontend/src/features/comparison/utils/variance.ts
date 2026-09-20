import type { SingleModelResult } from "@/types/inference";

export interface ModelComparisonMetrics {
  confidenceDelta: number;
  confidenceDeltaPercent: string;
  fasterModel: "lstm" | "bert" | "equal";
  latencyRatio: number;
  latencyDiffMs: number;
  parameterRatio: number;
  consensus: "AGREEMENT" | "DIVERGENCE";
  summaryText: string;
}

export function computeModelComparison(
  lstm?: SingleModelResult,
  bert?: SingleModelResult
): ModelComparisonMetrics | null {
  if (!lstm || !bert) return null;

  const confidenceDelta = Math.abs(bert.confidence - lstm.confidence);
  const confidenceDeltaPercent = `${(confidenceDelta * 100).toFixed(1)}%`;

  const latencyDiffMs = Math.abs(bert.latencyMs - lstm.latencyMs);
  const latencyRatio =
    lstm.latencyMs > 0 ? Number((bert.latencyMs / lstm.latencyMs).toFixed(1)) : 1;
  const fasterModel = lstm.latencyMs <= bert.latencyMs ? "lstm" : "bert";

  // BERT ~109.5M vs LSTM ~4.2M = ~26.1x
  const parameterRatio = 26.1;

  const consensus = bert.verdict === lstm.verdict ? "AGREEMENT" : "DIVERGENCE";

  let summaryText = "";
  if (consensus === "AGREEMENT") {
    summaryText = `Both architectures converge on a ${bert.verdict} verdict (Dual Unanimous Consensus). Bi-LSTM served ${latencyRatio}x faster with minimal footprint (~4.2M params), while BERT Transformer achieved higher feature resolution with 12 attention heads.`;
  } else {
    summaryText = `Architectural divergence detected! BERT classified as ${bert.verdict} (${(bert.confidence * 100).toFixed(1)}%), whereas Bi-LSTM classified as ${lstm.verdict} (${(lstm.confidence * 100).toFixed(1)}%). BERT's cross-attention mechanisms detect deeper contextual subtleties that sequential recurrent cells may smooth over.`;
  }

  return {
    confidenceDelta,
    confidenceDeltaPercent,
    fasterModel,
    latencyRatio,
    latencyDiffMs,
    parameterRatio,
    consensus,
    summaryText,
  };
}
