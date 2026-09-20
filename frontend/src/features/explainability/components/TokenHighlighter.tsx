import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { TokenAttention } from "../types";
import { SaliencyPopover } from "./SaliencyPopover";

export interface TokenHighlighterProps {
  tokens: TokenAttention[];
  threshold?: number; // 0.0 to 1.0
  className?: string;
  onTokenClick?: (token: TokenAttention) => void;
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
    <TooltipProvider delayDuration={100}>
      <div
        className={cn(
          "flex flex-wrap gap-x-1.5 gap-y-2 text-sm md:text-base leading-relaxed p-4 rounded-xl bg-zinc-950/50 border border-white/5 font-mono select-none",
          className
        )}
      >
        {tokens.map((item, index) => {
          // Unique key incorporating index to completely prevent React key collisions on repeated words
          const tokenKey = item.id ? `${item.id}-${index}` : `${item.token}-${index}`;
          const isAboveThreshold = item.weight >= threshold;
          const isReal = item.direction === "real";
          const isFake = item.direction === "fake";

          // Calculate dynamic opacity proportional to attention weight
          const opacity = Math.max(0.15, Math.min(0.85, item.weight));

          let bgClass = "bg-transparent text-zinc-300 border-transparent";

          if (isAboveThreshold) {
            if (isReal) {
              bgClass =
                "text-emerald-300 border-emerald-500/30 hover:border-emerald-400 hover:shadow-[0_0_12px_rgba(52,211,153,0.3)]";
            } else if (isFake) {
              bgClass =
                "text-rose-300 border-rose-500/30 hover:border-rose-400 hover:shadow-[0_0_12px_rgba(251,113,133,0.3)]";
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
                    !isAboveThreshold && "opacity-50 grayscale hover:opacity-100 hover:grayscale-0"
                  )}
                >
                  {item.token}
                </button>
              </TooltipTrigger>
              <TooltipContent side="top" className="p-0 border-0 bg-transparent shadow-none">
                <SaliencyPopover token={item} />
              </TooltipContent>
            </Tooltip>
          );
        })}
      </div>
    </TooltipProvider>
  );
}

export default TokenHighlighter;
