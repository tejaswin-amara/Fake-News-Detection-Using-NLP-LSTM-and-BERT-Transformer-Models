import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("Automated Accessibility (a11y) Audits - WCAG 2.1 AA", () => {
  test("Inference Studio should have zero critical or serious accessibility violations", async ({
    page,
  }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();

    const blockingViolations = accessibilityScanResults.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious"
    );

    expect(blockingViolations).toEqual([]);
  });

  test("Benchmarks Hub should have zero critical or serious accessibility violations", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /Benchmarks Hub/i }).click();
    await page.waitForLoadState("networkidle");

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();

    const blockingViolations = accessibilityScanResults.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious"
    );

    expect(blockingViolations).toEqual([]);
  });

  test("Explainability Lab should have zero critical or serious accessibility violations", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /Explainability Lab/i }).click();
    await page.waitForLoadState("networkidle");

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();

    const blockingViolations = accessibilityScanResults.violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious"
    );

    expect(blockingViolations).toEqual([]);
  });
});
