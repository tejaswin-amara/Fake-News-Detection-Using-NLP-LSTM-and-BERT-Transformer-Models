import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { SingleModelResult } from "@/types/inference";
import { ModelOutputCard } from "./ModelOutputCard";

const mockModel: SingleModelResult = {
  modelId: "bert",
  modelName: "Fine-Tuned BERT Transformer",
  verdict: "REAL",
  confidence: 0.965,
  probabilityReal: 0.965,
  probabilityFake: 0.035,
  latencyMs: 138.4,
  tokensCount: 42,
  paramCount: "~109.5M params",
  architecture: "BERT-base-uncased",
  saliencyTokens: [],
};

describe("ModelOutputCard", () => {
  it("renders model telemetry, name, verdict, and parameters", () => {
    render(<ModelOutputCard model={mockModel} highlighted={true} />);

    expect(screen.getByText(/BERT ARCHITECTURE/i)).toBeTruthy();
    expect(screen.getByText("Fine-Tuned BERT Transformer")).toBeTruthy();
    expect(screen.getByText("~109.5M params")).toBeTruthy();
    expect(screen.getByText(/P\(Real \| Evidence\):/i)).toBeTruthy();
    expect(screen.getByText(/P\(Deceptive \| Evidence\):/i)).toBeTruthy();
    expect(screen.getByText(/138\.4 ms/i)).toBeTruthy();
    expect(screen.getByText(/~1\.2 GB/i)).toBeTruthy();
  });
});
