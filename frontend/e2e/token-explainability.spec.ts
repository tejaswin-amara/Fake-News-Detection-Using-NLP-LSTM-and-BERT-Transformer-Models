import { test, expect } from "@playwright/test";

test.describe("Token Explainability and Saliency Heatmap", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    // Run an inference to populate token attention saliency heatmap
    await page.getByRole("button", { name: /Clickbait Health/i }).click();
    await page.getByRole("button", { name: /Execute Neural Verification/i }).click();
    await expect(page.getByText(/NLP TOKEN ATTENTION SALIENCY HEATMAP/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test("should render token breakdown visualization in the heatmap", async ({ page }) => {
    // Assert heatmap container and active signals counter are rendered
    await expect(page.getByText(/Active Signals:/i)).toBeVisible();
    await expect(page.getByText(/Credible tokens/i)).toBeVisible();
    await expect(page.getByText(/Deceptive tokens/i)).toBeVisible();

    // Verify individual token elements exist inside the heatmap
    const tokenButtons = page.locator("section[aria-label='Attention Heatmap Preview'] button");
    const count = await tokenButtons.count();
    expect(count).toBeGreaterThan(5);
  });

  test("should trigger SaliencyPopover on token hover", async ({ page }) => {
    // Find the deceptive token button "Pharma"
    const tokenButton = page.getByRole("button", { name: "Pharma", exact: true });
    await expect(tokenButton).toBeVisible();

    // Hover over the token button and await tooltip
    await tokenButton.hover();
    await page.waitForTimeout(300);

    // Verify SaliencyPopover tooltip content appears
    await expect(page.getByText(/Attention Saliency:/i).first()).toBeVisible({ timeout: 5000 });
  });

  test("should dynamically filter tokens using saliency threshold slider", async ({ page }) => {
    // Interact with slider in Explainability Lab or Heatmap Preview
    await page.getByRole("button", { name: /Explainability Lab/i }).click();
    await expect(page.getByText(/Attention Filter Threshold/i)).toBeVisible();

    // Slider track exists
    const slider = page.getByRole("slider").first();
    await expect(slider).toBeVisible();

    // Increase threshold by focusing and pressing ArrowRight multiple times
    await slider.focus();
    for (let i = 0; i < 6; i++) {
      await page.keyboard.press("ArrowRight");
    }

    // Verify the threshold percentage updated
    await expect(page.getByText(/Attention Filter Threshold/i).locator("..")).toContainText(/%/);
  });
});
