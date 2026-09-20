import { Trophy, Zap } from "lucide-react";
import { BENCHMARK_MODELS } from "../data/benchmarksData";

export function ComparativeMetricsTable() {
  return (
    <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
      <div>
        <h3 className="text-base font-bold text-white font-mono tracking-tight">
          CROSS-MODEL COMPARATIVE VALIDATION BENCHMARKS
        </h3>
        <p className="text-xs text-zinc-400">
          Empirical validation metrics computed across test datasets (F1 Macro, ROC-AUC, Brier
          Calibration, and Latency).
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs border-collapse">
          <thead>
            <tr className="border-b border-white/10 bg-zinc-900/60 text-zinc-400 uppercase text-[10px]">
              <th className="p-3">Model Architecture</th>
              <th className="p-3">Family</th>
              <th className="p-3 text-right">Accuracy</th>
              <th className="p-3 text-right">Precision</th>
              <th className="p-3 text-right">Recall</th>
              <th className="p-3 text-right text-indigo-400">F1 Score</th>
              <th className="p-3 text-right text-emerald-400">ROC-AUC</th>
              <th className="p-3 text-right">Brier Loss</th>
              <th className="p-3 text-right text-amber-400">Latency</th>
              <th className="p-3 text-right">Size</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {BENCHMARK_MODELS.map((model) => (
              <tr
                key={model.name}
                className={`hover:bg-white/[0.03] transition-colors ${
                  model.isChampion ? "bg-emerald-500/[0.03]" : ""
                }`}
              >
                <td className="p-3 font-bold text-white whitespace-nowrap">
                  <div className="flex items-center gap-1.5">
                    {model.isChampion && <Trophy className="size-3.5 text-amber-400 shrink-0" />}
                    <span>{model.name}</span>
                  </div>
                  <span className="text-[10px] text-zinc-500 block font-normal">{model.tag}</span>
                </td>
                <td className="p-3 text-zinc-400 whitespace-nowrap">{model.family}</td>
                <td className="p-3 text-right text-zinc-200">
                  {(model.accuracy * 100).toFixed(1)}%
                </td>
                <td className="p-3 text-right text-zinc-200">
                  {(model.precision * 100).toFixed(1)}%
                </td>
                <td className="p-3 text-right text-zinc-200">{(model.recall * 100).toFixed(1)}%</td>
                <td className="p-3 text-right font-bold text-indigo-300">
                  {model.f1Score.toFixed(4)}
                </td>
                <td className="p-3 text-right font-bold text-emerald-300">
                  {model.rocAuc.toFixed(4)}
                </td>
                <td className="p-3 text-right text-zinc-400">{model.brierScore.toFixed(4)}</td>
                <td className="p-3 text-right font-semibold text-amber-300 whitespace-nowrap">
                  <Zap className="inline size-3 mr-0.5 text-amber-400" />
                  {model.latencyMs < 1 ? "< 1 ms" : `${model.latencyMs} ms`}
                </td>
                <td className="p-3 text-right text-zinc-400 whitespace-nowrap">
                  {model.modelSizeMb >= 1
                    ? `${model.modelSizeMb} MB`
                    : `${(model.modelSizeMb * 1024).toFixed(0)} KB`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
