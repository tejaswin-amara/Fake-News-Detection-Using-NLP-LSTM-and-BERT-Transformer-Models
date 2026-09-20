import { test, expect } from "@playwright/test";

test.describe("Inference Studio User Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should load the application and render header and form", async ({ page }) => {
    await expect(page.locator("h1")).toContainText("VERITAS AI");
    await expect(page.getByRole("button", { name: /Inference Studio/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Explainability Lab/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Benchmarks Hub/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Audit Trail/i })).toBeVisible();
  });

  test("should load presets (Reuters Geopolitical and Clickbait Health)", async ({ page }) => {
    // Click Reuters Geopolitical preset
    const reutersPreset = page.getByRole("button", { name: /Reuters Geopolitical/i });
    await expect(reutersPreset).toBeVisible();
    await reutersPreset.click();

    const titleInput = page.locator("#article-title");
    const textArea = page.locator("#article-text");

    await expect(titleInput).toHaveValue(/Central Banks Coordinate Liquidity/i);
    await expect(textArea).toHaveValue(/Federal Reserve and four peer central banks/i);

    // Click Clickbait Health preset
    const clickbaitPreset = page.getByRole("button", { name: /Clickbait Health/i });
    await expect(clickbaitPreset).toBeVisible();
    await clickbaitPreset.click();

    await expect(titleInput).toHaveValue(/Ancient Himalayan Moss/i);
    await expect(textArea).toHaveValue(/Big Pharma is furiously trying to remove/i);
  });

  test("should execute inference and render dual-model comparison cards and gauges", async ({ page }) => {
    // Select Clickbait preset
    await page.getByRole("button", { name: /Clickbait Health/i }).click();

    // Trigger inference execution
    const runButton = page.getByRole("button", { name: /Execute Neural Verification/i });
    await expect(runButton).toBeVisible();
    await runButton.click();

    // Verify comparison section header and cards appear
    await expect(page.getByText(/DUAL-MODEL INFERENCE & ARCHITECTURAL COMPARISON/i)).toBeVisible({
      timeout: 10_000,
    });

    // Check for both model cards
    await expect(page.getByRole("heading", { name: "Fine-Tuned BERT Transformer" })).toBeVisible();
    await expect(page.getByRole("heading", { name: /GloVe \+ Stacked Bi-LSTM/i })).toBeVisible();

    // Check confidence gauges and verdicts
    await expect(page.getByText(/Consensus/i).first()).toBeVisible();
    await expect(page.getByText(/FAKE|DECEPTIVE/i).first()).toBeVisible();
  });

  test("should handle custom text input submission", async ({ page }) => {
    const titleInput = page.locator("#article-title");
    const textArea = page.locator("#article-text");

    await titleInput.fill("Custom Test Article Headline");
    await textArea.fill(
      "The official statistical bureau announced that consumer price index remained steady through the second quarter, matching forecasts."
    );

    const runButton = page.getByRole("button", { name: /Execute Neural Verification/i });
    await runButton.click();

    await expect(page.getByText(/DUAL-MODEL INFERENCE & ARCHITECTURAL COMPARISON/i)).toBeVisible({
      timeout: 10_000,
    });
    await expect(page.getByRole("heading", { name: "Fine-Tuned BERT Transformer" })).toBeVisible();
  });
});
