import { useEffect, useState } from "react";
import type { DualModelComparisonResult } from "@/types/inference";

const STORAGE_KEY = "veritas_inference_audit_trail_v1";
const MAX_HISTORY_ITEMS = 50;

const memoryStore = new Map<string, string>();

function getSafeStorage(): {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
  removeItem: (key: string) => void;
} {
  try {
    if (typeof window !== "undefined" && window.localStorage) {
      window.localStorage.setItem("__veritas_probe__", "1");
      window.localStorage.removeItem("__veritas_probe__");
      return window.localStorage;
    }
  } catch {
    // LocalStorage restricted or in Node test runner
  }

  return {
    getItem: (key: string) => memoryStore.get(key) ?? null,
    setItem: (key: string, value: string) => {
      memoryStore.set(key, value);
    },
    removeItem: (key: string) => {
      memoryStore.delete(key);
    },
  };
}

export function loadHistory(): DualModelComparisonResult[] {
  try {
    const storage = getSafeStorage();
    const raw = storage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

export function saveHistoryItem(item: DualModelComparisonResult): DualModelComparisonResult[] {
  try {
    const storage = getSafeStorage();
    const current = loadHistory();
    const updated = [item, ...current.filter((x) => x.id !== item.id)].slice(0, MAX_HISTORY_ITEMS);
    storage.setItem(STORAGE_KEY, JSON.stringify(updated));
    return updated;
  } catch {
    return [];
  }
}

export function clearHistory(): void {
  try {
    const storage = getSafeStorage();
    storage.removeItem(STORAGE_KEY);
  } catch {}
}

export function deleteHistoryItem(id: string): DualModelComparisonResult[] {
  try {
    const storage = getSafeStorage();
    const current = loadHistory();
    const updated = current.filter((x) => x.id !== id);
    storage.setItem(STORAGE_KEY, JSON.stringify(updated));
    return updated;
  } catch {
    return [];
  }
}

export function useHistoryStore() {
  const [history, setHistory] = useState<DualModelComparisonResult[]>([]);

  useEffect(() => {
    setHistory(loadHistory());
  }, []);

  const addRecord = (item: DualModelComparisonResult) => {
    const updated = saveHistoryItem(item);
    setHistory(updated);
  };

  const removeRecord = (id: string) => {
    const updated = deleteHistoryItem(id);
    setHistory(updated);
  };

  const clearAll = () => {
    clearHistory();
    setHistory([]);
  };

  return {
    history,
    addRecord,
    removeRecord,
    clearAll,
  };
}
