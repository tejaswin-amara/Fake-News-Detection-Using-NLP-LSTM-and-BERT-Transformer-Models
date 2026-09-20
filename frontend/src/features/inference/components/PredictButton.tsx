import { ArrowRight, Loader2, Sparkles } from "lucide-react";
import { MagnetButton } from "@/components/react-bits/MagnetButton";
import { cn } from "@/lib/utils";

interface PredictButtonProps {
  isLoading: boolean;
  loadingStep?: string;
  disabled?: boolean;
  type?: "submit" | "button" | "reset";
  onClick?: () => void;
  className?: string;
}

export function PredictButton({
  isLoading,
  loadingStep = "Running inference pass...",
  disabled,
  type = "submit",
  onClick,
  className,
}: PredictButtonProps) {
  return (
    <MagnetButton
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      className={cn(
        "w-full sm:w-auto px-8 py-3.5 text-sm font-mono font-bold uppercase tracking-wider rounded-xl transition-all duration-300",
        isLoading
          ? "bg-zinc-800 text-zinc-400 cursor-wait border border-white/10"
          : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_25px_rgba(99,102,241,0.4)] hover:shadow-[0_0_35px_rgba(99,102,241,0.6)] border border-indigo-400/40",
        className
      )}
    >
      {isLoading ? (
        <span className="flex items-center gap-2">
          <Loader2 className="size-4 animate-spin text-indigo-400" />
          <span>{loadingStep}</span>
        </span>
      ) : (
        <span className="flex items-center gap-2">
          <Sparkles className="size-4" />
          <span>Execute Neural Verification</span>
          <ArrowRight className="size-4 opacity-70" />
        </span>
      )}
    </MagnetButton>
  );
}
