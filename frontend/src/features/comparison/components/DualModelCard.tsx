import { Activity, Cpu, Layers, Zap } from "lucide-react";
import { AnimatedCounter } from "@/components/react-bits/AnimatedCounter";
import { SpotlightCard } from "@/components/react-bits/SpotlightCard";
import { TextScramble } from "@/components/react-bits/TextScramble";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { SingleModelResult } from "@/types/inference";
import { DifferentialConfidenceGauge } from "./DifferentialConfidenceGauge";

interface DualModelCardProps {
  model: SingleModelResult;
  highlighted?: boolean;
}

export function DualModelCard({ model, highlighted }: DualModelCardProps) {
  const isReal = model.verdict === "REAL";
  const isFake = model.verdict === "FAKE";

  let statusGlow =
    "border-amber-500/30 text-amber-400 bg-amber-500/10 shadow-[0_0_20px_rgba(251,191,36,0.2)]";
  let spotlightColor = "rgba(251, 191, 36, 0.15)";
  let verdictText = "UNCERTAIN AMBIGUITY";

  if (isReal) {
    statusGlow =
      "border-emerald-500/40 text-emerald-400 bg-emerald-500/10 shadow-[0_0_25px_rgba(52,211,153,0.25)]";
    spotlightColor = "rgba(52, 211, 153, 0.15)";
    verdictText = "VERIFIED CREDIBLE";
  } else if (isFake) {
    statusGlow =
      "border-rose-500/40 text-rose-400 bg-rose-500/10 shadow-[0_0_25px_rgba(251,113,133,0.25)]";
    spotlightColor = "rgba(251, 113, 133, 0.15)";
    verdictText = "FLAGGED AS DECEPTIVE";
  }

  return (
    <SpotlightCard
      spotlightColor={spotlightColor}
      className={cn(
        "p-6 flex flex-col justify-between transition-all duration-300",
        highlighted && "ring-1 ring-indigo-500/50"
      )}
    >
      <div>
        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-mono tracking-wider uppercase text-zinc-400">
                {model.modelId.toUpperCase()} ARCHITECTURE
              </span>
              <Badge
                variant="outline"
                className="text-[10px] py-0 px-2 border-white/10 text-zinc-300 bg-white/5"
              >
                {model.paramCount}
              </Badge>
            </div>
            <h3 className="text-xl font-bold text-white tracking-tight">{model.modelName}</h3>
          </div>
          <div
            className={cn(
              "px-3 py-1.5 rounded-full border text-xs font-mono font-bold tracking-wide flex items-center gap-1.5",
              statusGlow
            )}
          >
            <span className="relative flex h-2 w-2">
              <span
                className={cn(
                  "animate-ping absolute inline-flex h-full w-full rounded-full opacity-75",
                  isReal ? "bg-emerald-400" : isFake ? "bg-rose-400" : "bg-amber-400"
                )}
              />
              <span
                className={cn(
                  "relative inline-flex rounded-full h-2 w-2",
                  isReal ? "bg-emerald-500" : isFake ? "bg-rose-500" : "bg-amber-500"
                )}
              />
            </span>
            <TextScramble text={verdictText} speed={25} />
          </div>
        </div>

        {/* Center: Confidence Gauge and Probability Distribution */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-6 items-center bg-zinc-900/40 p-4 rounded-xl border border-white/5">
          <div className="flex justify-center">
            <DifferentialConfidenceGauge
              confidence={model.confidence}
              verdict={model.verdict}
              size={130}
              strokeWidth={9}
              label="Confidence"
            />
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div>
              <div className="flex justify-between text-zinc-400 mb-1">
                <span>P(Real | Evidence):</span>
                <span className="text-emerald-400 font-semibold">
                  <AnimatedCounter value={model.probabilityReal * 100} decimals={2} suffix="%" />
                </span>
              </div>
              <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-emerald-400 rounded-full transition-all duration-1000"
                  style={{ width: `${model.probabilityReal * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-zinc-400 mb-1">
                <span>P(Deceptive | Evidence):</span>
                <span className="text-rose-400 font-semibold">
                  <AnimatedCounter value={model.probabilityFake * 100} decimals={2} suffix="%" />
                </span>
              </div>
              <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-rose-400 rounded-full transition-all duration-1000"
                  style={{ width: `${model.probabilityFake * 100}%` }}
                />
              </div>
            </div>

            <div className="pt-2 border-t border-white/5 flex items-center justify-between text-zinc-400 text-[11px]">
              <span>Classification Margin:</span>
              <span className="text-zinc-200 font-bold">
                {Math.abs((model.probabilityReal - model.probabilityFake) * 100).toFixed(1)}% delta
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Telemetry Footer */}
      <div className="pt-4 border-t border-white/10 space-y-2">
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-white/5">
            <div className="flex items-center justify-center gap-1 text-zinc-400 text-[10px] uppercase font-mono">
              <Zap className="size-3 text-amber-400" />
              <span>Latency</span>
            </div>
            <div className="text-sm font-bold font-mono text-zinc-200 mt-1">
              <AnimatedCounter value={model.latencyMs} decimals={1} suffix=" ms" />
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-white/5">
            <div className="flex items-center justify-center gap-1 text-zinc-400 text-[10px] uppercase font-mono">
              <Layers className="size-3 text-indigo-400" />
              <span>Tokens</span>
            </div>
            <div className="text-sm font-bold font-mono text-zinc-200 mt-1">
              <AnimatedCounter value={model.tokensCount} decimals={0} />
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-white/5">
            <div className="flex items-center justify-center gap-1 text-zinc-400 text-[10px] uppercase font-mono">
              <Cpu className="size-3 text-emerald-400" />
              <span>Memory</span>
            </div>
            <div className="text-sm font-bold font-mono text-zinc-200 mt-1">
              {model.modelId === "bert" ? "~1.2 GB" : "~350 MB"}
            </div>
          </div>
        </div>

        <p className="text-[11px] text-zinc-500 italic truncate font-mono pt-1">
          <Activity className="inline size-3 mr-1 text-zinc-400" />
          {model.architecture}
        </p>
      </div>
    </SpotlightCard>
  );
}
