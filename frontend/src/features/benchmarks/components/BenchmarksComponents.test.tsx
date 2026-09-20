import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";
import { LossGraph } from "./LossGraph";
import { MetricsRadar } from "./MetricsRadar";

afterEach(() => {
  cleanup();
});

describe("BenchmarksHub Components", () => {
  describe("MetricsRadar", () => {
    it("renders radar SVG chart and dimension labels", () => {
      render(<MetricsRadar />);
      expect(screen.getByText(/MULTI-DIMENSIONAL ARCHITECTURE RADAR/i)).toBeTruthy();
      expect(screen.getAllByText("Accuracy").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Precision").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Recall").length).toBeGreaterThan(0);
      expect(screen.getAllByText("F1-Score").length).toBeGreaterThan(0);
      expect(screen.getAllByText("ROC-AUC").length).toBeGreaterThan(0);
    });

    it("allows toggling model visibility chips", async () => {
      const user = userEvent.setup();
      render(<MetricsRadar />);

      const bertChips = screen.getAllByRole("button", { name: /Fine-Tuned/i });
      expect(bertChips.length).toBeGreaterThan(0);
      await user.click(bertChips[0]);
      expect(screen.getByText(/MULTI-DIMENSIONAL ARCHITECTURE RADAR/i)).toBeTruthy();
    });
  });

  describe("LossGraph", () => {
    it("renders loss convergence chart with model tabs", () => {
      render(<LossGraph />);
      expect(screen.getByText(/TRAINING & VALIDATION LOSS CONVERGENCE/i)).toBeTruthy();
      expect(screen.getByText(/Training Loss \(Cross-Entropy\)/i)).toBeTruthy();
      expect(screen.getByText(/Validation Loss \(Holdout\)/i)).toBeTruthy();
    });

    it("switches to Bi-LSTM 10 epochs when selected", async () => {
      const user = userEvent.setup();
      render(<LossGraph />);

      const lstmTabs = screen.getAllByRole("tab", { name: /Bi-LSTM/i });
      expect(lstmTabs.length).toBeGreaterThan(0);
      await user.click(lstmTabs[0]);

      expect(screen.getByText(/E10/i)).toBeTruthy();
      expect(screen.getByText(/Gradient clipping at norm 1.0/i)).toBeTruthy();
    });
  });
});
