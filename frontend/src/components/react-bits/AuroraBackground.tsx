import type React from "react";
import { cn } from "@/lib/utils";

interface AuroraBackgroundProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
  showRadialGradient?: boolean;
}

export function AuroraBackground({
  className,
  children,
  showRadialGradient = true,
  ...props
}: AuroraBackgroundProps) {
  return (
    <div
      className={cn(
        "relative flex min-h-screen flex-col items-center justify-start overflow-hidden bg-[#030712] text-zinc-100 transition-bg",
        className
      )}
      {...props}
    >
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          aria-hidden="true"
          className={cn(
            "filter blur-[80px] opacity-40 will-change-transform",
            "absolute -inset-[10px]",
            "[--white-gradient:repeating-linear-gradient(100deg,var(--white)_0%,var(--white)_7%,var(--transparent)_10%,var(--transparent)_12%,var(--white)_16%)]",
            "[--dark-gradient:repeating-linear-gradient(100deg,#000_0%,#000_7%,transparent_10%,transparent_12%,#000_16%)]",
            "[--aurora:repeating-linear-gradient(100deg,#6366f1_10%,#3b82f6_15%,#10b981_20%,#8b5cf6_25%,#6366f1_30%)]",
            "[background-image:var(--dark-gradient),var(--aurora)]",
            "[background-size:300%,_200%]",
            "[background-position:50%_50%,50%_50%]",
            "animate-aurora"
          )}
        />
        {showRadialGradient && (
          <div
            aria-hidden="true"
            className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-950/20 via-[#030712]/80 to-[#030712]"
          />
        )}
      </div>
      <div className="relative z-10 w-full">{children}</div>
    </div>
  );
}
