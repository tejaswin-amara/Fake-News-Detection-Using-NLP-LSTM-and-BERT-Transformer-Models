import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { DualModelComparisonResult } from "@/types/inference";
import { ExportModal } from "./ExportModal";

const mockItem: DualModelComparisonResult = {
  id: "audit-test-123",
  timestamp: "2026-09-19T20:00:00.000Z",
  title: "Test Verification Headline",
  text: "Sample article text for audit inspection and export validation.",
  targetModel: "both",
  consensus: "AGREEMENT",
  bert: {
    modelId: "bert",
    modelName: "Fine-Tuned BERT Transformer",
    verdict: "REAL",
    confidence: 0.945,
    probabilityReal: 0.945,
    probabilityFake: 0.055,
    latencyMs: 142.1,
    tokensCount: 9,
    paramCount: "~109.5M params",
    architecture: "BERT-base-uncased",
    saliencyTokens: [],
  },
  lstm: {
    modelId: "lstm",
    modelName: "GloVe + Stacked BiLSTM",
    verdict: "REAL",
    confidence: 0.885,
    probabilityReal: 0.885,
    probabilityFake: 0.115,
    latencyMs: 19.3,
    tokensCount: 9,
    paramCount: "~4.2M params",
    architecture: "Bi-LSTM 2-Layer",
    saliencyTokens: [],
  },
  isSimulated: true,
};

describe("ExportModal", () => {
  it("renders export modal with Markdown, JSON, and CSV tabs", async () => {
    const user = userEvent.setup();
    const handleOpenChange = vi.fn();

    render(<ExportModal open={true} onOpenChange={handleOpenChange} item={mockItem} />);

    expect(screen.getByText(/EXPORT AUDIT REPORT/i)).toBeTruthy();
    expect(screen.getByText(/Markdown Summary/i)).toBeTruthy();
    expect(screen.getByText(/Raw JSON/i)).toBeTruthy();
    expect(screen.getByText(/Spreadsheet CSV/i)).toBeTruthy();

    // Verify CSV tab displays structured CSV
    const csvTab = screen.getByRole("tab", { name: /Spreadsheet CSV/i });
    await user.click(csvTab);

    expect(screen.getByText(/id,timestamp,model,verdict/i)).toBeTruthy();
    expect(screen.getByRole("button", { name: /Download \.csv/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /Copy CSV/i })).toBeTruthy();
  });
});
