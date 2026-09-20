import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

// Global ResizeObserver mock for Radix UI primitives (Slider, Tabs) in JSDOM
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

if (typeof global !== "undefined" && !global.ResizeObserver) {
  global.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver;
}

if (typeof window !== "undefined") {
  if (!window.ResizeObserver) {
    window.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver;
  }

  // Global matchMedia mock for responsive queries and components in JSDOM
  if (!window.matchMedia) {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  }
}
