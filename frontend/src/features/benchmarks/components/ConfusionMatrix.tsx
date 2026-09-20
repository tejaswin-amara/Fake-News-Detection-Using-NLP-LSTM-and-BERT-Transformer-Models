import { useState } from "react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { BENCHMARK_MODELS } from "../data/benchmarksData";

export function ConfusionMatrix() {
  const [selectedModelIndex, setSelectedModelIndex] = useState(0); // 0 = BERT, 1 = LSTM
  const model = BENCHMARK_MODELS[selectedModelIndex] ?? BENCHMARK_MODELS[0];
  const { tp, fp, fn, tn } = model.confusionMatrix;
  const total = tp + fp + fn + tn;

  const tpRate = ((tp / (tp + fn)) * 100).toFixed(1);
  const fpRate = ((fp / (fp + tn)) * 100).toFixed(1);
  const fnRate = ((fn / (tp + fn)) * 100).toFixed(1);
  const tnRate = ((tn / (fp + tn)) * 100).toFixed(1);

  return (
    <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-white font-mono tracking-tight">
            EMPIRICAL CONFUSION MATRIX (2x2)
          </h3>
          <p className="text-xs text-zinc-400">
            Evaluating {total.toLocaleString()} test articles under held-out empirical validation.
          </p>
        </div>

        <Tabs
          value={String(selectedModelIndex)}
          onValueChange={(val) => setSelectedModelIndex(Number(val))}
        >
          <TabsList className="bg-zinc-900 border border-white/10">
            <TabsTrigger value="0" className="text-xs font-mono">
              BERT Transformer
            </TabsTrigger>
            <TabsTrigger value="1" className="text-xs font-mono">
              Bi-LSTM Recurrent
            </TabsTrigger>
            <TabsTrigger value="2" className="text-xs font-mono">
              L2 Champion
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <TooltipProvider delayDuration={100}>
        <div className="flex flex-col items-center justify-center p-4">
          <div className="grid grid-cols-2 gap-3 max-w-md w-full">
            {/* True Positive: Predicted Fake, Actually Fake */}
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-center hover:border-rose-400 hover:shadow-[0_0_20px_rgba(251,113,133,0.2)] transition-all cursor-pointer">
                  <span className="text-[10px] font-mono text-rose-300 uppercase tracking-wider block">
                    True Positives (TP)
                  </span>
                  <div className="text-2xl font-bold font-mono text-rose-400 my-1">{tp}</div>
                  <span className="text-xs font-mono text-zinc-400">{tpRate}% Recall Rate</span>
                </div>
              </TooltipTrigger>
              <TooltipContent className="glass-panel-elevated p-2 text-xs border border-white/10 text-zinc-200">
                Correctly identified deceptive news articles (Hit).
              </TooltipContent>
            </Tooltip>

            {/* False Positive: Predicted Fake, Actually Real */}
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-center hover:border-amber-400 hover:shadow-[0_0_20px_rgba(251,191,36,0.2)] transition-all cursor-pointer">
                  <span className="text-[10px] font-mono text-amber-300 uppercase tracking-wider block">
                    False Positives (FP)
                  </span>
                  <div className="text-2xl font-bold font-mono text-amber-400 my-1">{fp}</div>
                  <span className="text-xs font-mono text-zinc-400">{fpRate}% False Alarm</span>
                </div>
              </TooltipTrigger>
              <TooltipContent className="glass-panel-elevated p-2 text-xs border border-white/10 text-zinc-200">
                Credible articles mistakenly flagged as deceptive (Type I error).
              </TooltipContent>
            </Tooltip>

            {/* False Negative: Predicted Real, Actually Fake */}
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-center hover:border-amber-400 hover:shadow-[0_0_20px_rgba(251,191,36,0.2)] transition-all cursor-pointer">
                  <span className="text-[10px] font-mono text-amber-300 uppercase tracking-wider block">
                    False Negatives (FN)
                  </span>
                  <div className="text-2xl font-bold font-mono text-amber-400 my-1">{fn}</div>
                  <span className="text-xs font-mono text-zinc-400">
                    {fnRate}% Missed Deception
                  </span>
                </div>
              </TooltipTrigger>
              <TooltipContent className="glass-panel-elevated p-2 text-xs border border-white/10 text-zinc-200">
                Deceptive articles that slipped through as credible (Type II error).
              </TooltipContent>
            </Tooltip>

            {/* True Negative: Predicted Real, Actually Real */}
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-center hover:border-emerald-400 hover:shadow-[0_0_20px_rgba(52,211,153,0.2)] transition-all cursor-pointer">
                  <span className="text-[10px] font-mono text-emerald-300 uppercase tracking-wider block">
                    True Negatives (TN)
                  </span>
                  <div className="text-2xl font-bold font-mono text-emerald-400 my-1">{tn}</div>
                  <span className="text-xs font-mono text-zinc-400">
                    {tnRate}% Specificity Rate
                  </span>
                </div>
              </TooltipTrigger>
              <TooltipContent className="glass-panel-elevated p-2 text-xs border border-white/10 text-zinc-200">
                Correctly validated credible news articles.
              </TooltipContent>
            </Tooltip>
          </div>
        </div>
      </TooltipProvider>

      <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono pt-3 border-t border-white/5">
        <div className="p-2 rounded bg-zinc-900/60">
          <span className="text-zinc-500 text-[10px] uppercase block">Overall Accuracy</span>
          <span className="font-bold text-white">{(model.accuracy * 100).toFixed(1)}%</span>
        </div>
        <div className="p-2 rounded bg-zinc-900/60">
          <span className="text-zinc-500 text-[10px] uppercase block">Macro Precision</span>
          <span className="font-bold text-emerald-400">{(model.precision * 100).toFixed(1)}%</span>
        </div>
        <div className="p-2 rounded bg-zinc-900/60">
          <span className="text-zinc-500 text-[10px] uppercase block">Macro F1 Score</span>
          <span className="font-bold text-indigo-400">{model.f1Score.toFixed(4)}</span>
        </div>
      </div>
    </div>
  );
}
