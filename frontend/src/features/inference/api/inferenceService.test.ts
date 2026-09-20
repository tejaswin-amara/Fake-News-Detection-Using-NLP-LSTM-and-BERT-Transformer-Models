import { describe, expect, it } from "vitest";
import { SAMPLE_ARTICLES } from "../data/sampleArticles";
import { simulateInference, tokenizeAndCalculateAttention } from "./inferenceService";

describe("Token Attention Saliency Engine", () => {
  it("extracts tokens and identifies sensationalist lexical triggers with deceptive direction", () => {
    const text = "Shocking secret miracle cure discovered by whistleblower!";
    const tokens = tokenizeAndCalculateAttention(text, "bert");

    expect(tokens.length).toBeGreaterThan(0);

    const shockingToken = tokens.find((t) => /shocking/i.test(t.token));
    expect(shockingToken).toBeDefined();
    expect(shockingToken?.direction).toBe("fake");
    expect(shockingToken?.weight).toBeGreaterThan(0.7);
    expect(shockingToken?.rawScore).toBeLessThan(0);

    const miracleToken = tokens.find((t) => /miracle/i.test(t.token));
    expect(miracleToken?.direction).toBe("fake");
  });

  it("identifies credible institutional markers with positive real attribution", () => {
    const text = "The Federal Reserve announced coordinated liquidity facilities.";
    const tokens = tokenizeAndCalculateAttention(text, "lstm");

    const reserveToken = tokens.find((t) => /reserve/i.test(t.token));
    expect(reserveToken).toBeDefined();
    expect(reserveToken?.direction).toBe("real");
    expect(reserveToken?.weight).toBeGreaterThan(0.7);
    expect(reserveToken?.rawScore).toBeGreaterThan(0);

    const announcedToken = tokens.find((t) => /announced/i.test(t.token));
    expect(announcedToken?.direction).toBe("real");
  });

  it("handles empty or single word text safely", () => {
    const emptyTokens = tokenizeAndCalculateAttention("", "bert");
    expect(emptyTokens).toEqual([]);

    const singleToken = tokenizeAndCalculateAttention("Report", "lstm");
    expect(singleToken.length).toBe(1);
    expect(singleToken[0]?.token).toBe("Report");
  });
});

describe("Deterministic Inference Simulation Engine", () => {
  it("accurately classifies credible news preset as REAL", () => {
    const credibleArticle = SAMPLE_ARTICLES.find((a) => a.category === "credible");
    expect(credibleArticle).toBeDefined();

    if (!credibleArticle) return;

    const result = simulateInference(credibleArticle.title, credibleArticle.text, "both");

    expect(result.bert?.verdict).toBe("REAL");
    expect(result.lstm?.verdict).toBe("REAL");
    expect(result.consensus).toBe("AGREEMENT");
    expect(result.bert?.confidence).toBeGreaterThan(0.65);
    expect(result.lstm?.confidence).toBeGreaterThan(0.65);
    expect(result.isSimulated).toBe(true);
  });

  it("accurately flags satirical and clickbait presets as FAKE", () => {
    const clickbaitArticle = SAMPLE_ARTICLES.find((a) => a.category === "clickbait");
    expect(clickbaitArticle).toBeDefined();

    if (!clickbaitArticle) return;

    const result = simulateInference(clickbaitArticle.title, clickbaitArticle.text, "both");

    expect(result.bert?.verdict).toBe("FAKE");
    expect(result.lstm?.verdict).toBe("FAKE");
    expect(result.consensus).toBe("AGREEMENT");
    expect(result.bert?.probabilityFake).toBeGreaterThan(0.65);
  });

  it("verifies telemetry constraints: BERT has more parameters and higher latency than Bi-LSTM", () => {
    const result = simulateInference(
      "Headline Test",
      "Sample body text for telemetry validation.",
      "both"
    );

    expect(result.bert).toBeDefined();
    expect(result.lstm).toBeDefined();

    if (result.bert && result.lstm) {
      expect(result.bert.latencyMs).toBeGreaterThan(result.lstm.latencyMs);
      expect(result.bert.paramCount).toContain("109.5M");
      expect(result.lstm.paramCount).toContain("4.2M");
      expect(result.differentialConfidence).toBeDefined();
      expect(result.differentialConfidence).toBeGreaterThanOrEqual(0);
    }
  });

  it("respects single-model targeting mode", () => {
    const bertOnly = simulateInference("Title", "Body text content for inference testing.", "bert");
    expect(bertOnly.bert).toBeDefined();
    expect(bertOnly.lstm).toBeUndefined();

    const lstmOnly = simulateInference("Title", "Body text content for inference testing.", "lstm");
    expect(lstmOnly.lstm).toBeDefined();
    expect(lstmOnly.bert).toBeUndefined();
  });
});
