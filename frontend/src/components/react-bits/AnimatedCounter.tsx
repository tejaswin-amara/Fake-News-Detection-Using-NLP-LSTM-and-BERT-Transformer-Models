import { animate, useMotionValue } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface AnimatedCounterProps {
  value: number;
  duration?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
}

export function AnimatedCounter({
  value,
  duration = 0.8,
  decimals = 0,
  prefix = "",
  suffix = "",
  className,
}: AnimatedCounterProps) {
  const [displayValue, setDisplayValue] = useState<string>(() => {
    return Number.isFinite(value) ? value.toFixed(decimals) : "0";
  });
  const motionVal = useMotionValue(0);
  const prevValue = useRef(0);

  useEffect(() => {
    if (!Number.isFinite(value)) return;
    const controls = animate(motionVal, value, {
      duration,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (latest) => {
        setDisplayValue(latest.toFixed(decimals));
      },
    });

    prevValue.current = value;

    return () => controls.stop();
  }, [value, duration, decimals, motionVal]);

  return (
    <span className={cn("font-mono font-semibold tabular-nums", className)}>
      {prefix}
      {displayValue}
      {suffix}
    </span>
  );
}
