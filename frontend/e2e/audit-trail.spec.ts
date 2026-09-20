import { test, expect } from "@playwright/test";

test.describe("Audit Trail & Persistence Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should persist verification records in localStorage across page reloads", async ({ page }) => {
    // Run an inference
    await page.getByRole("button", { name: /Clickbait Health/i }).click();
    await page.getByRole("button", { name: /Execute Neural Verification/i }).click();

    // Wait for completion
    await expect(page.getByText(/DUAL-MODEL INFERENCE & ARCHITECTURAL COMPARISON/i)).toBeVisible({
      timeout: 10_000,
    });

    // Navigate to Audit Trail tab
    await page.getByRole("button", { name: /Audit Trail/i }).click();
    await expect(page.getByText(/PERSISTENT LOCAL INFERENCE AUDIT TRAIL/i)).toBeVisible();
    await expect(page.getByText(/Ancient Himalayan Moss/i)).toBeVisible();

    // Reload the page
    await page.reload();

    // Check that record is still present in Audit Trail after reload
    await page.getByRole("button", { name: /Audit Trail/i }).click();
    await expect(page.getByText(/PERSISTENT LOCAL INFERENCE AUDIT TRAIL/i)).toBeVisible();
    await expect(page.getByText(/Ancient Himalayan Moss/i)).toBeVisible();
  });

  test("should open the Export Modal and support JSON, Markdown, and CSV views", async ({ page }) => {
    // Seed an inference record
    await page.getByRole("button", { name: /Reuters Geopolitical/i }).click();
    await page.getByRole("button", { name: /Execute Neural Verification/i }).click();
    await expect(page.getByText(/DUAL-MODEL INFERENCE & ARCHITECTURAL COMPARISON/i)).toBeVisible({
      timeout: 10_000,
    });

    // Open Audit Trail
    await page.getByRole("button", { name: /Audit Trail/i }).click();
    await expect(page.getByText(/PERSISTENT LOCAL INFERENCE AUDIT TRAIL/i)).toBeVisible();

    // Click Export button (accessible name "Export report")
    const exportButton = page.getByRole("button", { name: "Export report" }).first();
    await expect(exportButton).toBeVisible();
    await exportButton.click();

    // Verify modal dialog opened
    await expect(page.getByText(/EXPORT AUDIT REPORT/i)).toBeVisible();
    await expect(page.getByRole("tab", { name: /Raw JSON/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /Markdown Summary/i })).toBeVisible();
    await expect(page.getByRole("tab", { name: /Spreadsheet CSV/i })).toBeVisible();

    // Switch to JSON tab and check content
    const jsonTab = page.getByRole("tab", { name: /Raw JSON/i });
    await jsonTab.click();
    await expect(page.getByText(/"targetModel"/i).first()).toBeVisible();

    // Switch to Markdown tab and check content
    const mdTab = page.getByRole("tab", { name: /Markdown Summary/i });
    await mdTab.click();
    await expect(page.getByText(/# VERITAS AI Verification Audit Report/i)).toBeVisible();

    // Switch to CSV tab and check content
    const csvTab = page.getByRole("tab", { name: /Spreadsheet CSV/i });
    await csvTab.click();
    await expect(page.getByText(/id,timestamp,model,verdict/i)).toBeVisible();

    // Check copy action
    const copyButton = page.getByRole("button", { name: /Copy/i }).first();
    await expect(copyButton).toBeVisible();
  });
});
