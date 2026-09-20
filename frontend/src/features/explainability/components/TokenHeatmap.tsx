import { Eye, Info, SlidersHorizontal, Sparkles } from "lucide-react";
import { useState } from "react";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { SingleModelResult } from "@/types/inference";
import { TokenHighlighter } from "./TokenHighlighter";
import { WeightScale } from "./WeightScale";

interface TokenHeatmapProps {
  lstm?: SingleModelResult;
  bert?: SingleModelResult;
}

export function TokenHeatmap({ lstm, bert }: TokenHeatmapProps) {
  const defaultModel = bert ? "bert" : "lstm";
  const [selectedModel, setSelectedModel] = useState<"bert" | "lstm">(defaultModel);
  const [threshold, setThreshold] = useState<number>(0.2); // Default to showing tokens >= 20% saliency

  const activeModel = selectedModel === "bert" ? bert : lstm;
  const tokens = activeModel?.saliencyTokens || [];

  const realTokensCount = tokens.filter((t) => t.direction === "real").length;
  const fakeTokensCount = tokens.filter((t) => t.direction === "fake").length;
  const filteredTokensCount = tokens.filter((t) => t.weight >= threshold).length;

  return (
    <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-6">
      {/* Header with Title and Model Switcher */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="size-4 text-indigo-400" />
            <h3 className="text-lg font-bold text-white font-mono tracking-tight">
              NLP TOKEN ATTENTION SALIENCY HEATMAP
            </h3>
          </div>
          <p className="text-xs text-zinc-400">
            Bidirectional gradient attribution showing token-level probability pulls toward Credible
            or Deceptive veracity.
          </p>
        </div>

        {lstm && bert && (
          <Tabs
            value={selectedModel}
            onValueChange={(val) => setSelectedModel(val as "bert" | "lstm")}
            className="w-auto"
          >
            <TabsList className="bg-zinc-900 border border-white/10">
              <TabsTrigger value="bert" className="text-xs font-mono font-semibold">
                BERT Attention (12-Head)
              </TabsTrigger>
              <TabsTrigger value="lstm" className="text-xs font-mono font-semibold">
                Bi-LSTM Recurrent Gradient
              </TabsTrigger>
            </TabsList>
          </Tabs>
        )}
      </div>

      {/* Saliency Filter Slider and Stats */}
      <div className="p-4 rounded-xl bg-zinc-900/60 border border-white/5 space-y-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-3 w-full md:w-80">
            <SlidersHorizontal className="size-4 text-zinc-400 shrink-0" />
            <div className="w-full space-y-1">
              <div className="flex justify-between text-xs font-mono text-zinc-300">
                <span>Attention Filter Threshold</span>
                <span className="text-indigo-400 font-bold">{(threshold * 100).toFixed(0)}%</span>
              </div>
              <Slider
                value={[threshold * 100]}
                min={0}
                max={90}
                step={5}
                onValueChange={(vals) => setThreshold((vals[0] ?? 20) / 100)}
                className="cursor-pointer"
              />
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
            <div className="px-2.5 py-1 rounded-lg bg-zinc-800/80 border border-white/5 flex items-center gap-2">
              <Eye className="size-3.5 text-zinc-400" />
              <span className="text-zinc-400">Active Signals:</span>
              <span className="text-white font-bold">
                {filteredTokensCount} / {tokens.length}
              </span>
            </div>
            <div className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              {realTokensCount} Credible tokens
            </div>
            <div className="px-2.5 py-1 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400">
              {fakeTokensCount} Deceptive tokens
            </div>
          </div>
        </div>

        <WeightScale />
      </div>

      {/* Interactive Token Highlighter */}
      <div>
        <TokenHighlighter tokens={tokens} threshold={threshold} />
      </div>

      <div className="flex items-center gap-2 text-xs text-zinc-500 font-mono">
        <Info className="size-3.5 text-zinc-400 shrink-0" />
        <span>
          Hover any highlighted token to view normalized saliency weight, log-odds attribution
          impact, and lexical trigger rationale.
        </span>
      </div>
    </div>
  );
}
