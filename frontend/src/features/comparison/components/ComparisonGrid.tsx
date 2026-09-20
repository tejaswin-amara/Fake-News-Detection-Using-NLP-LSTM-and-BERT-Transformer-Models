import { AlertTriangle, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { SingleModelResult } from "@/types/inference";
import { computeModelComparison } from "../utils/variance";
import { DualModelCard } from "./DualModelCard";

interface ComparisonGridProps {
  lstm?: SingleModelResult;
  bert?: SingleModelResult;
}

export function ComparisonGrid({ lstm, bert }: ComparisonGridProps) {
  if (!lstm && !bert) {
    return (
      <div className="glass-panel p-8 rounded-2xl text-center text-zinc-500 font-mono text-sm border border-dashed border-white/10">
        Run an analysis to inspect side-by-side model predictions and architectural divergence.
      </div>
    );
  }

  const comparison = computeModelComparison(lstm, bert);
  const isConsensus = comparison?.consensus === "AGREEMENT";

  return (
    <div className="space-y-6">
      {/* Consensus & Comparative Telemetry Banner */}
      {comparison && lstm && bert && (
        <div className="glass-panel p-4 md:p-6 rounded-2xl border border-white/10 relative overflow-hidden">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div
                className={`p-2.5 rounded-xl border ${
                  isConsensus
                    ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400 glow-emerald"
                    : "bg-amber-500/10 border-amber-500/30 text-amber-400 glow-amber"
                }`}
              >
                {isConsensus ? (
                  <CheckCircle2 className="size-6" />
                ) : (
                  <AlertTriangle className="size-6" />
                )}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-base font-bold text-white font-mono tracking-tight">
                    MODEL CONSENSUS: {comparison.consensus}
                  </h4>
                  <span
                    className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded-full font-bold border ${
                      isConsensus
                        ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                        : "bg-amber-500/20 text-amber-300 border-amber-500/40"
                    }`}
                  >
                    {isConsensus ? "Dual Unanimous" : "Cross-Architecture Divergence"}
                  </span>
                </div>
                <p className="text-xs text-zinc-400 mt-1 max-w-2xl leading-relaxed">
                  {comparison.summaryText}
                </p>
              </div>
            </div>

            {/* Micro Differential Stats */}
            <div className="flex items-center gap-4 bg-zinc-900/80 p-3 rounded-xl border border-white/5 font-mono text-xs self-stretch md:self-auto justify-around">
              <div>
                <span className="text-[10px] text-zinc-500 uppercase block">Confidence Delta</span>
                <span className="text-sm font-bold text-indigo-400">
                  {comparison.confidenceDeltaPercent}
                </span>
              </div>
              <div className="h-6 w-px bg-white/10" />
              <div>
                <span className="text-[10px] text-zinc-500 uppercase block">Inference Speedup</span>
                <span className="text-sm font-bold text-emerald-400">
                  {comparison.latencyRatio}x faster (LSTM)
                </span>
              </div>
              <div className="h-6 w-px bg-white/10" />
              <div>
                <span className="text-[10px] text-zinc-500 uppercase block">Param Ratio</span>
                <span className="text-sm font-bold text-zinc-300">
                  {comparison.parameterRatio}x (BERT)
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Grid of Dual Model Cards */}
      <div
        className={cn(
          "grid gap-6",
          lstm && bert ? "grid-cols-1 lg:grid-cols-2" : "grid-cols-1 max-w-2xl mx-auto"
        )}
      >
        {lstm && <DualModelCard model={lstm} />}
        {bert && <DualModelCard model={bert} highlighted />}
      </div>
    </div>
  );
}
