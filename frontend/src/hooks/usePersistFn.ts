import { useRef } from "react";

// biome-ignore lint/suspicious/noExplicitAny: standard higher-order function generic parameter constraint
type noop = (...args: any[]) => any;

/**
 * usePersistFn instead of useCallback to reduce cognitive load
 */
export function usePersistFn<T extends noop>(fn: T): T {
  const fnRef = useRef<T>(fn);
  fnRef.current = fn;

  const persistFn = useRef<T | null>(null);
  if (!persistFn.current) {
    persistFn.current = function (this: unknown, ...args: unknown[]) {
      // biome-ignore lint/suspicious/noExplicitAny: forwarding args
      return (fnRef.current as any)?.apply(this, args);
    } as T;
  }

  return (persistFn.current ?? fn) as T;
}
