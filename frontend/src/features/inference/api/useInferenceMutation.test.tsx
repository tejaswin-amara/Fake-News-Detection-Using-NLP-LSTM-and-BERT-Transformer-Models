import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import type React from "react";
import { describe, expect, it } from "vitest";
import { useInferenceMutation } from "./useInferenceMutation";

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe("useInferenceMutation", () => {
  it("executes simulated inference mutation and updates query cache", async () => {
    const { result } = renderHook(() => useInferenceMutation(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isPending).toBe(false);

    await act(async () => {
      const data = await result.current.mutateAsync({
        title: "Test News Headline",
        text: "Federal Reserve announced new liquidity facility according to joint central bank statements.",
        targetModel: "both",
      });

      expect(data).toBeTruthy();
      expect(data.title).toBe("Test News Headline");
      expect(data.bert?.verdict).toBe("REAL");
      expect(data.lstm?.verdict).toBe("REAL");
      expect(data.consensus).toBe("AGREEMENT");
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});
