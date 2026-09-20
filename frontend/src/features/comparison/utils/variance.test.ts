import { describe, expect, it } from "vitest";
import type { SingleModelResult } from "@/types/inference";
import { computeModelComparison } from "./variance";

describe("Model Variance and Comparison Calculations", () => {
  const mockLstm: SingleModelResult = {
    modelId: "lstm",
    modelName: "GloVe + Bi-LSTM",
    verdict: "REAL",
    confidence: 0.82,
    probabilityFake: 0.18,
    probabilityReal: 0.82,
    latencyMs: 18.0,
    tokensCount: 50,
    paramCount: "~4.2M params",
    architecture: "Bi-LSTM 2-Layer",
    saliencyTokens: [],
  };

  const mockBert: SingleModelResult = {
    modelId: "bert",
    modelName: "BERT Transformer",
    verdict: "REAL",
    confidence: 0.94,
    probabilityFake: 0.06,
    probabilityReal: 0.94,
    latencyMs: 144.0,
    tokensCount: 50,
    paramCount: "~109.5M params",
    architecture: "BERT-base-uncased",
    saliencyTokens: [],
  };

  it("calculates confidence delta and speedup ratio accurately for unanimous consensus", () => {
    const comparison = computeModelComparison(mockLstm, mockBert);

    expect(comparison).not.toBeNull();
    expect(comparison?.consensus).toBe("AGREEMENT");
    expect(comparison?.confidenceDelta).toBeCloseTo(0.12, 2);
    expect(comparison?.confidenceDeltaPercent).toBe("12.0%");
    expect(comparison?.fasterModel).toBe("lstm");
    expect(comparison?.latencyRatio).toBe(8.0); // 144 / 18 = 8.0
    expect(comparison?.summaryText).toContain("Dual Unanimous");
  });

  it("detects architectural divergence when verdicts clash", () => {
    const divergingLstm: SingleModelResult = {
      ...mockLstm,
      verdict: "FAKE",
      confidence: 0.75,
      probabilityFake: 0.75,
      probabilityReal: 0.25,
    };

    const comparison = computeModelComparison(divergingLstm, mockBert);

    expect(comparison).not.toBeNull();
    expect(comparison?.consensus).toBe("DIVERGENCE");
    expect(comparison?.summaryText).toContain("Architectural divergence detected");
  });

  it("returns null if either model is missing", () => {
    expect(computeModelComparison(undefined, mockBert)).toBeNull();
    expect(computeModelComparison(mockLstm, undefined)).toBeNull();
  });
});
