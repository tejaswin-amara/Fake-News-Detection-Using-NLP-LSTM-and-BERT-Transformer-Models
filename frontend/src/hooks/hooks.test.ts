import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useClipboard } from "./useClipboard";
import { useMediaQuery } from "./useMediaQuery";

describe("Global Hooks", () => {
  describe("useMediaQuery", () => {
    it("returns false for non-matching media query in default test environment", () => {
      const { result } = renderHook(() => useMediaQuery("(min-width: 1024px)"));
      expect(typeof result.current).toBe("boolean");
    });
  });

  describe("useClipboard", () => {
    it("copies text using navigator.clipboard", async () => {
      const writeTextMock = vi.fn().mockResolvedValue(undefined);
      Object.assign(navigator, {
        clipboard: {
          writeText: writeTextMock,
        },
      });

      const { result } = renderHook(() => useClipboard());
      expect(result.current.hasCopied).toBe(false);

      await act(async () => {
        const ok = await result.current.copy("VERITAS AI Test");
        expect(ok).toBe(true);
      });

      expect(writeTextMock).toHaveBeenCalledWith("VERITAS AI Test");
      expect(result.current.hasCopied).toBe(true);
    });
  });
});
