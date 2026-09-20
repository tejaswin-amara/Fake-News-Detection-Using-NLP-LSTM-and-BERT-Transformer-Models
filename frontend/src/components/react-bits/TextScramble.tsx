import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface TextScrambleProps {
  text: string;
  className?: string;
  speed?: number;
  trigger?: boolean | number | string;
  scrambleChars?: string;
  onComplete?: () => void;
}

const DEFAULT_CHARS = "!<>-_\\/[]{}—=+*^?#________";

export function TextScramble({
  text,
  className,
  speed = 30,
  trigger = true,
  scrambleChars = DEFAULT_CHARS,
  onComplete,
}: TextScrambleProps) {
  const [displayText, setDisplayText] = useState(text);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (!trigger) {
      setDisplayText(text);
      return;
    }

    let iteration = 0;
    const targetLength = text.length;

    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
    }

    const intervalId = window.setInterval(() => {
      setDisplayText(() => {
        return text
          .split("")
          .map((char, index) => {
            if (char === " ") return " ";
            if (index < iteration) {
              return text[index];
            }
            return scrambleChars[Math.floor(Math.random() * scrambleChars.length)];
          })
          .join("");
      });

      if (iteration >= targetLength) {
        window.clearInterval(intervalId);
        onComplete?.();
      }

      iteration += 1 / 2;
    }, speed);

    intervalRef.current = intervalId;

    return () => {
      window.clearInterval(intervalId);
    };
  }, [text, speed, scrambleChars, trigger, onComplete]);

  return <span className={cn("font-mono font-bold tracking-wider", className)}>{displayText}</span>;
}
