import { useCallback, useState } from "react";

export interface UseClipboardOptions {
  timeout?: number;
}

export function useClipboard(options: UseClipboardOptions = {}) {
  const { timeout = 2000 } = options;
  const [hasCopied, setHasCopied] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const copy = useCallback(
    async (text: string) => {
      if (!navigator?.clipboard) {
        // Fallback for environments lacking navigator.clipboard
        try {
          const textArea = document.createElement("textarea");
          textArea.value = text;
          textArea.style.position = "fixed";
          textArea.style.opacity = "0";
          document.body.appendChild(textArea);
          textArea.focus();
          textArea.select();
          const successful = document.execCommand("copy");
          document.body.removeChild(textArea);
          if (!successful) throw new Error("Fallback copy command failed");
          setHasCopied(true);
          setTimeout(() => setHasCopied(false), timeout);
          return true;
        } catch (err) {
          setError(err instanceof Error ? err : new Error(String(err)));
          return false;
        }
      }

      try {
        await navigator.clipboard.writeText(text);
        setHasCopied(true);
        setError(null);
        setTimeout(() => setHasCopied(false), timeout);
        return true;
      } catch (err) {
        setError(err instanceof Error ? err : new Error(String(err)));
        return false;
      }
    },
    [timeout]
  );

  return { copy, hasCopied, error };
}

export default useClipboard;
