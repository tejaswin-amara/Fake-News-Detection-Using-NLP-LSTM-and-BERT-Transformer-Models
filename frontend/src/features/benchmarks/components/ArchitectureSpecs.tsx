import { Check, Layers, Network } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ARCHITECTURE_DETAILS } from "../data/benchmarksData";

export function ArchitectureSpecs() {
  return (
    <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-6">
      <div>
        <h3 className="text-base font-bold text-white font-mono tracking-tight flex items-center gap-2">
          <Network className="size-4 text-indigo-400" />
          PIPELINE ARCHITECTURE & HYPERPARAMETER SPECIFICATION
        </h3>
        <p className="text-xs text-zinc-400 mt-0.5">
          Structural comparison between Recurrent Neural Network (GloVe + Bi-LSTM) and
          Self-Attention Transformer (Fine-Tuned BERT).
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs border-collapse">
          <thead>
            <tr className="border-b border-white/10 bg-zinc-900/60 text-zinc-400 uppercase text-[10px]">
              <th className="p-3">Component Layer</th>
              <th className="p-3 text-rose-400">GloVe + Stacked Bi-LSTM</th>
              <th className="p-3 text-indigo-400">Fine-Tuned BERT Transformer</th>
              <th className="p-3 text-zinc-300">Architectural Rationale</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {ARCHITECTURE_DETAILS.map((spec) => (
              <tr key={spec.layer} className="hover:bg-white/[0.02] transition-colors">
                <td className="p-3 font-bold text-white whitespace-nowrap flex items-center gap-1.5">
                  <Layers className="size-3.5 text-zinc-500" />
                  {spec.layer}
                </td>
                <td className="p-3 text-zinc-300 max-w-xs">{spec.lstmConfig}</td>
                <td className="p-3 text-zinc-300 max-w-xs">{spec.bertConfig}</td>
                <td className="p-3 text-zinc-400 text-[11px] leading-relaxed max-w-sm">
                  {spec.rationale}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-white/5 text-xs font-mono">
        <div className="p-4 rounded-xl bg-zinc-900/50 border border-rose-500/20 space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-rose-400">Bi-LSTM Deployment Profile</h4>
            <Badge variant="outline" className="border-rose-500/30 text-rose-300 bg-rose-500/10">
              Edge & Stream Capable
            </Badge>
          </div>
          <ul className="space-y-1.5 text-zinc-400 text-[11px]">
            <li className="flex items-center gap-1.5">
              <Check className="size-3 text-emerald-400" />
              <span>Lightweight parameter count (~4.2M) enables instant cold starts.</span>
            </li>
            <li className="flex items-center gap-1.5">
              <Check className="size-3 text-emerald-400" />
              <span>Sub-20ms inference satisfies real-time ingestion pipelines.</span>
            </li>
            <li className="flex items-center gap-1.5">
              <Check className="size-3 text-emerald-400" />
              <span>Zero external tokenization latency; fast n-gram lookups.</span>
            </li>
          </ul>
        </div>

        <div className="p-4 rounded-xl bg-zinc-900/50 border border-indigo-500/20 space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-indigo-400">BERT Transformer Profile</h4>
            <Badge
              variant="outline"
              className="border-indigo-500/30 text-indigo-300 bg-indigo-500/10"
            >
              Authoritative Arbiter
            </Badge>
          </div>
          <ul className="space-y-1.5 text-zinc-400 text-[11px]">
            <li className="flex items-center gap-1.5">
              <Check className="size-3 text-emerald-400" />
              <span>12 self-attention heads detect subtle linguistic irony and sarcasm.</span>
            </li>
            <li className="flex items-center gap-1.5">
              <Check className="size-3 text-emerald-400" />
              <span>Higher discriminative F1 score (0.875) minimizes false negative risk.</span>
            </li>
            <li className="flex items-center gap-1.5">
              <Check className="size-3 text-emerald-400" />
              <span>Attention weights directly map cross-sentence rhetorical dependencies.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
