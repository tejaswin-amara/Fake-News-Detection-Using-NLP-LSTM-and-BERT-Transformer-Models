import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SaliencyPopover } from "./SaliencyPopover";

describe("SaliencyPopover", () => {
  it("renders token details with credible signal styling", () => {
    render(
      <SaliencyPopover
        token={{
          token: "Reuters",
          weight: 0.88,
          direction: "real",
          rawScore: 1.408,
          reason: "Primary news agency wire attribution",
        }}
      />
    );

    expect(screen.getByText('"Reuters"')).toBeTruthy();
    expect(screen.getByText(/real signal/i)).toBeTruthy();
    expect(screen.getByText("88.0%")).toBeTruthy();
    expect(screen.getByText("+1.408")).toBeTruthy();
    expect(screen.getByText(/Primary news agency wire attribution/i)).toBeTruthy();
  });

  it("renders deceptive signal details with negative impact score", () => {
    render(
      <SaliencyPopover
        token={{
          token: "Miracle",
          weight: 0.92,
          direction: "fake",
          rawScore: -1.656,
          reason: "High sensationalism lexical trigger",
        }}
      />
    );

    expect(screen.getByText('"Miracle"')).toBeTruthy();
    expect(screen.getByText(/fake signal/i)).toBeTruthy();
    expect(screen.getByText("92.0%")).toBeTruthy();
    expect(screen.getByText("-1.656")).toBeTruthy();
  });
});
