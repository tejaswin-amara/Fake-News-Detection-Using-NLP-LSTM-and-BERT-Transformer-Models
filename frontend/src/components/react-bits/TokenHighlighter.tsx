import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

export interface TokenSaliency {
  id?: string;
  token: string;
  weight: number; // 0.0 to 1.0 normalized saliency
  direction: "real" | "fake" | "neutral";
  rawScore?: number;
  reason?: string;
}

interface TokenHighlighterProps {
  tokens: TokenSaliency[];
  threshold?: number; // 0.0 to 1.0 (filter tokens below threshold)
  className?: string;
  onTokenClick?: (token: TokenSaliency) => void;
}

export function TokenHighlighter({
  tokens,
  threshold = 0.0,
  className,
  onTokenClick,
}: TokenHighlighterProps) {
  if (!tokens || tokens.length === 0) {
    return <p className="text-sm text-zinc-500 italic">No token attention data available.</p>;
  }

  return (
    <TooltipProvider delayDuration={150}>
      <div
        className={cn(
          "flex flex-wrap gap-x-1.5 gap-y-2 text-sm md:text-base leading-relaxed p-4 rounded-xl bg-zinc-950/50 border border-white/5 font-mono",
          className
        )}
      >
        {tokens.map((item, index) => {
          const tokenKey = item.id ? `${item.id}-${index}` : `${item.token}-${index}`;
          const isAboveThreshold = item.weight >= threshold;
          const isReal = item.direction === "real";
          const isFake = item.direction === "fake";

          // Calculate dynamic opacity proportional to weight
          const opacity = Math.max(0.15, Math.min(0.85, item.weight));

          let bgClass = "bg-transparent text-zinc-300 border-transparent";
          let badgeClass = "text-zinc-400";

          if (isAboveThreshold) {
            if (isReal) {
              bgClass =
                "text-emerald-300 border-emerald-500/30 hover:border-emerald-400 hover:shadow-[0_0_12px_rgba(52,211,153,0.3)]";
              badgeClass = "text-emerald-400";
            } else if (isFake) {
              bgClass =
                "text-rose-300 border-rose-500/30 hover:border-rose-400 hover:shadow-[0_0_12px_rgba(251,113,133,0.3)]";
              badgeClass = "text-rose-400";
            } else {
              bgClass = "text-zinc-200 border-zinc-700/50";
            }
          }

          const inlineBg = isAboveThreshold
            ? isReal
              ? `rgba(16, 185, 129, ${opacity * 0.4})`
              : isFake
                ? `rgba(244, 63, 94, ${opacity * 0.4})`
                : "rgba(39, 39, 42, 0.3)"
            : "transparent";

          return (
            <Tooltip key={tokenKey}>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  onClick={() => onTokenClick?.(item)}
                  style={{ backgroundColor: inlineBg }}
                  className={cn(
                    "relative px-1.5 py-0.5 rounded border transition-all duration-150 cursor-pointer font-medium text-left",
                    bgClass,
                    !isAboveThreshold && "opacity-60 grayscale hover:opacity-100 hover:grayscale-0"
                  )}
                >
                  {item.token}
                </button>
              </TooltipTrigger>
              <TooltipContent
                side="top"
                className="glass-panel-elevated p-3 text-xs border border-white/10 rounded-xl shadow-xl max-w-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-mono font-bold text-white text-sm">"{item.token}"</span>
                    <span
                      className={cn(
                        "text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded border",
                        isReal
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                          : isFake
                            ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                            : "bg-zinc-800 text-zinc-400 border-zinc-700"
                      )}
                    >
                      {item.direction} signal
                    </span>
                  </div>
                  <div className="flex items-center justify-between gap-4 text-zinc-400 pt-1">
                    <span>Saliency Weight:</span>
                    <span className="font-mono font-bold text-zinc-200">
                      {(item.weight * 100).toFixed(1)}%
                    </span>
                  </div>
                  {item.rawScore !== undefined && (
                    <div className="flex items-center justify-between gap-4 text-zinc-400">
                      <span>Attribution Impact:</span>
                      <span className={cn("font-mono font-semibold", badgeClass)}>
                        {item.rawScore > 0
                          ? `+${item.rawScore.toFixed(3)}`
                          : item.rawScore.toFixed(3)}
                      </span>
                    </div>
                  )}
                  {item.reason && (
                    <p className="text-[11px] text-zinc-300 pt-1 border-t border-white/5">
                      {item.reason}
                    </p>
                  )}
                </div>
              </TooltipContent>
            </Tooltip>
          );
        })}
      </div>
    </TooltipProvider>
  );
}
