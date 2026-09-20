export function WeightScale() {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs font-mono p-3 rounded-xl bg-zinc-900/50 border border-white/5">
      <div className="flex items-center gap-2">
        <span className="inline-block w-3 h-3 rounded bg-emerald-500/80 border border-emerald-400" />
        <span className="text-emerald-400 font-semibold">Credible Attributions (Real)</span>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-zinc-500">Threshold:</span>
        <div className="w-28 h-2 rounded-full bg-gradient-to-r from-emerald-500 via-zinc-600 to-rose-500 opacity-70" />
      </div>

      <div className="flex items-center gap-2">
        <span className="inline-block w-3 h-3 rounded bg-rose-500/80 border border-rose-400" />
        <span className="text-rose-400 font-semibold">Deceptive Attributions (Fake)</span>
      </div>
    </div>
  );
}
