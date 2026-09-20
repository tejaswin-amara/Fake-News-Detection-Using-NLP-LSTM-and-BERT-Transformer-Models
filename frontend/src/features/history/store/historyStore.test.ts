// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from "vitest";
import type { DualModelComparisonResult } from "@/types/inference";
import { clearHistory, deleteHistoryItem, loadHistory, saveHistoryItem } from "./historyStore";

describe("History Store LocalStorage Sync", () => {
  beforeEach(() => {
    clearHistory();
  });

  const sampleResult: DualModelComparisonResult = {
    id: "test-rec-1",
    timestamp: new Date().toISOString(),
    title: "Breaking Financial Report",
    text: "Federal reserve statements on liquidity.",
    targetModel: "both",
    consensus: "AGREEMENT",
    isSimulated: true,
  };

  it("stores and retrieves inference results in LIFO order", () => {
    saveHistoryItem(sampleResult);

    const secondResult: DualModelComparisonResult = {
      ...sampleResult,
      id: "test-rec-2",
      title: "Second Report",
    };
    saveHistoryItem(secondResult);

    const records = loadHistory();
    expect(records.length).toBe(2);
    expect(records[0]?.id).toBe("test-rec-2");
    expect(records[1]?.id).toBe("test-rec-1");
  });

  it("deletes a record by ID", () => {
    saveHistoryItem(sampleResult);
    expect(loadHistory().length).toBe(1);

    deleteHistoryItem("test-rec-1");
    expect(loadHistory().length).toBe(0);
  });

  it("clears all records completely", () => {
    saveHistoryItem(sampleResult);
    clearHistory();
    expect(loadHistory()).toEqual([]);
  });
});
