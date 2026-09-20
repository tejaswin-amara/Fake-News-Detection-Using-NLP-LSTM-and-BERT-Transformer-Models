import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { TokenAttention } from "../types";

export interface SaliencyPopoverProps {
  token: TokenAttention;
  className?: string;
}

export function SaliencyPopover({ token, className }: SaliencyPopoverProps) {
  const isReal = token.direction === "real";
  const isFake = token.direction === "fake";

  return (
    <div
      className={cn(
        "glass-panel-elevated p-3.5 text-xs border border-white/10 rounded-xl shadow-2xl max-w-xs space-y-2 font-mono text-zinc-200",
        className
      )}
    >
      <div className="flex items-center justify-between gap-3 pb-1 border-b border-white/10">
        <span className="font-mono font-bold text-white text-sm tracking-wide">
          "{token.token}"
        </span>
        <Badge
          variant="outline"
          className={cn(
            "text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded border",
            isReal
              ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/40"
              : isFake
                ? "bg-rose-500/15 text-rose-300 border-rose-500/40"
                : "bg-zinc-800 text-zinc-400 border-zinc-700"
          )}
        >
          {token.direction} signal
        </Badge>
      </div>

      <div className="space-y-1 text-[11px]">
        <div className="flex items-center justify-between text-zinc-400">
          <span>Attention Saliency:</span>
          <span className="font-bold text-white font-mono">{(token.weight * 100).toFixed(1)}%</span>
        </div>
        <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-300",
              isReal ? "bg-emerald-400" : isFake ? "bg-rose-400" : "bg-zinc-500"
            )}
            style={{ width: `${Math.min(100, token.weight * 100)}%` }}
          />
        </div>
      </div>

      {token.rawScore !== undefined && (
        <div className="flex items-center justify-between text-zinc-400 text-[11px]">
          <span>Attribution Impact:</span>
          <span
            className={cn(
              "font-mono font-bold",
              isReal ? "text-emerald-400" : isFake ? "text-rose-400" : "text-zinc-300"
            )}
          >
            {token.rawScore > 0 ? `+${token.rawScore.toFixed(3)}` : token.rawScore.toFixed(3)}
          </span>
        </div>
      )}

      {token.reason && (
        <p className="text-[10px] text-zinc-400 pt-1 border-t border-white/5 italic leading-relaxed">
          {token.reason}
        </p>
      )}
    </div>
  );
}

export default SaliencyPopover;
