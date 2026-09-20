import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { Providers } from "./providers";

// Mock canvas-confetti
vi.mock("canvas-confetti", () => ({
  default: vi.fn(),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("VERITAS App Integration & UI Components", () => {
  it("renders header, navigation tabs, and quick presets correctly", () => {
    render(
      <Providers>
        <App />
      </Providers>
    );

    expect(screen.getByText(/VERITAS AI/i)).toBeTruthy();
    expect(screen.getByRole("button", { name: /Inference Studio/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /Explainability Lab/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /Benchmarks Hub/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /Audit Trail/i })).toBeTruthy();

    expect(screen.getByText(/The Onion Satire/i)).toBeTruthy();
    expect(screen.getByText(/Reuters Geopolitical Report/i)).toBeTruthy();
  });

  it("loads article preset when clicked and enables execution button", async () => {
    const user = userEvent.setup();
    render(
      <Providers>
        <App />
      </Providers>
    );

    const presetBtn = screen.getByRole("button", { name: /The Onion Satire/i });
    await user.click(presetBtn);

    const textarea = screen.getByPlaceholderText(
      /Paste complete news article/i
    ) as HTMLTextAreaElement;
    expect(textarea.value).toContain("HOUSTON");

    const execBtn = screen.getByRole("button", { name: /Execute Neural Verification/i });
    expect(execBtn).toBeTruthy();
    expect(execBtn.hasAttribute("disabled")).toBe(false);

    // Verify clicking the execution button submits the form and runs inference
    await user.click(execBtn);

    // After inference completes, model verdict cards and attention heatmap are rendered
    expect(
      await screen.findByText(/NLP TOKEN ATTENTION SALIENCY HEATMAP/i, {}, { timeout: 4000 })
    ).toBeTruthy();
  });

  it("switches to Benchmarks Hub tab and displays comparative metrics, radar, and loss graphs", async () => {
    const user = userEvent.setup();
    render(
      <Providers>
        <App />
      </Providers>
    );

    const benchmarksTab = screen.getByRole("button", { name: /Benchmarks Hub/i });
    await user.click(benchmarksTab);

    expect(screen.getByText(/EMPIRICAL EVALUATION & BENCHMARKS HUB/i)).toBeTruthy();
    expect(screen.getAllByText(/Fine-Tuned BERT/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/GloVe \+ Stacked BiLSTM/i).length).toBeGreaterThan(0);

    // Check Metrics Radar tab
    const radarTab = screen.getByRole("tab", { name: /Metrics Radar/i });
    expect(radarTab).toBeTruthy();
    await user.click(radarTab);
    expect(screen.getByText(/MULTI-DIMENSIONAL ARCHITECTURE RADAR/i)).toBeTruthy();

    // Check Loss Convergence tab
    const lossTab = screen.getByRole("tab", { name: /Loss Convergence/i });
    expect(lossTab).toBeTruthy();
    await user.click(lossTab);
    expect(screen.getByText(/TRAINING & VALIDATION LOSS CONVERGENCE/i)).toBeTruthy();
  });
});
