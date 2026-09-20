import { motion } from "framer-motion";
import { AnimatedCounter } from "@/components/react-bits/AnimatedCounter";
import { cn } from "@/lib/utils";
import type { VeracityVerdict } from "@/types/inference";

interface DifferentialConfidenceGaugeProps {
  confidence: number; // 0 to 1
  verdict: VeracityVerdict;
  size?: number;
  strokeWidth?: number;
  label?: string;
  showLabel?: boolean;
  className?: string;
}

export function DifferentialConfidenceGauge({
  confidence,
  verdict,
  size = 140,
  strokeWidth = 10,
  label = "Confidence",
  showLabel = true,
  className,
}: DifferentialConfidenceGaugeProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - confidence * circumference;

  let strokeColor = "#818cf8"; // Indigo default
  let glowColor = "rgba(129, 140, 248, 0.4)";
  let textColor = "text-indigo-400";

  if (verdict === "REAL") {
    strokeColor = "#34d399"; // Emerald
    glowColor = "rgba(52, 211, 153, 0.4)";
    textColor = "text-emerald-400";
  } else if (verdict === "FAKE") {
    strokeColor = "#fb7185"; // Rose/Crimson
    glowColor = "rgba(251, 113, 133, 0.4)";
    textColor = "text-rose-400";
  } else if (verdict === "UNCERTAIN") {
    strokeColor = "#fbbf24"; // Amber
    glowColor = "rgba(251, 191, 36, 0.4)";
    textColor = "text-amber-400";
  }

  return (
    <div className={cn("flex flex-col items-center justify-center relative", className)}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          className="rotate-[-90deg] overflow-visible"
          aria-label={`${label}: ${(confidence * 100).toFixed(1)}%`}
          role="img"
        >
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress circle */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            strokeLinecap="round"
            fill="transparent"
            style={{
              filter: `drop-shadow(0 0 8px ${glowColor})`,
            }}
          />
        </svg>

        {/* Center score readout */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className={cn("text-2xl font-bold font-mono tracking-tight", textColor)}>
            <AnimatedCounter value={confidence * 100} decimals={1} suffix="%" duration={1.2} />
          </div>
          {showLabel && (
            <span className="text-[10px] uppercase font-mono tracking-widest text-zinc-400 mt-0.5">
              {label}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
