import { test, expect } from "@playwright/test";

test.describe("Empirical Benchmarks Hub Navigation", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    // Navigate to Benchmarks Hub
    await page.getByRole("button", { name: /Benchmarks Hub/i }).click();
  });

  test("should render the Benchmarks Hub header and sub-tabs", async ({ page }) => {
    await expect(page.getByText(/EMPIRICAL EVALUATION & BENCHMARKS HUB/i)).toBeVisible();
    await expect(page.getByRole("tab", { name: /Comparative Metrics/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /Metrics Radar/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /Loss Convergence/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /Confusion Matrix/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /ROC-AUC Curves/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /Architecture Specs/i })).toBeVisible();
  });

  test("should render the 5-axis metrics radar", async ({ page }) => {
    await page.getByRole("tab", { name: /Metrics Radar/i }).click();
    // Verify radar chart container and heading
    await expect(page.getByText(/MULTI-DIMENSIONAL ARCHITECTURE RADAR/i)).toBeVisible();
    await expect(page.locator("svg").first()).toBeVisible();
  });

  test("should render multi-epoch loss graph", async ({ page }) => {
    await page.getByRole("tab", { name: /Loss Convergence/i }).click();
    // Verify loss convergence chart heading and SVG line chart
    await expect(page.getByText(/TRAINING & VALIDATION LOSS CONVERGENCE/i)).toBeVisible();
    await expect(page.locator("svg").first()).toBeVisible();
  });

  test("should render 2x2 confusion matrix", async ({ page }) => {
    await page.getByRole("tab", { name: /Confusion Matrix/i }).click();
    // Verify 2x2 matrix cells: True Positive, True Negative, False Positive, False Negative
    await expect(page.getByText(/EMPIRICAL CONFUSION MATRIX/i)).toBeVisible();
    await expect(page.getByText(/True Positives/i).first()).toBeVisible();
    await expect(page.getByText(/True Negatives/i).first()).toBeVisible();
    await expect(page.getByText(/False Positives/i).first()).toBeVisible();
    await expect(page.getByText(/False Negatives/i).first()).toBeVisible();
  });

  test("should render ROC-AUC curves", async ({ page }) => {
    await page.getByRole("tab", { name: /ROC-AUC Curves/i }).click();
    // Verify ROC chart heading and AUC legends
    await expect(page.getByText(/RECEIVER OPERATING CHARACTERISTIC/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /BERT Transformer/i })).toBeVisible();
  });
});
