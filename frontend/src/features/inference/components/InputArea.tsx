import { zodResolver } from "@hookform/resolvers/zod";
import { AlertCircle, ClipboardCheck, Eraser, Sparkles } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import type { ArticlePreset, ModelTarget } from "@/types/inference";
import { SAMPLE_ARTICLES } from "../data/sampleArticles";
import { PredictButton } from "./PredictButton";

export const inferenceFormSchema = z.object({
  title: z.string().max(300, "Title cannot exceed 300 characters").optional(),
  text: z
    .string()
    .min(10, "Article content must be at least 10 characters long")
    .max(50000, "Article content cannot exceed 50,000 characters"),
  targetModel: z.enum(["lstm", "bert", "both"]),
});

export type InferenceFormValues = z.infer<typeof inferenceFormSchema>;

interface InputAreaProps {
  onSubmit: (values: InferenceFormValues) => void;
  isLoading: boolean;
  loadingStep?: string;
  initialValues?: Partial<InferenceFormValues>;
}

export function InputArea({ onSubmit, isLoading, loadingStep, initialValues }: InputAreaProps) {
  const [selectedPresetId, setSelectedPresetId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<InferenceFormValues>({
    resolver: zodResolver(inferenceFormSchema),
    defaultValues: {
      title: initialValues?.title ?? "",
      text: initialValues?.text ?? "",
      targetModel: initialValues?.targetModel ?? "both",
    },
  });

  const textValue = watch("text") || "";
  const titleValue = watch("title") || "";
  const targetModel = watch("targetModel");

  const wordCount = textValue.trim() ? textValue.trim().split(/\s+/).length : 0;
  const charCount = textValue.length;

  const handleApplyPreset = (preset: ArticlePreset) => {
    setSelectedPresetId(preset.id);
    setValue("title", preset.title, { shouldValidate: true });
    setValue("text", preset.text, { shouldValidate: true });
  };

  const handleCleanPaste = async () => {
    try {
      const clipboardText = await navigator.clipboard.readText();
      if (!clipboardText) return;
      // Sanitize zero-width characters, multiple consecutive empty lines
      const cleaned = clipboardText
        .replace(/[\u200B-\u200D\uFEFF]/g, "")
        .replace(/[ \t]+/g, " ")
        .replace(/\n{3,}/g, "\n\n")
        .trim();
      setValue("text", cleaned, { shouldValidate: true });
    } catch {
      // Clipboard permissions denied
    }
  };

  const handleClear = () => {
    reset({
      title: "",
      text: "",
      targetModel: "both",
    });
    setSelectedPresetId(null);
  };

  return (
    <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-6">
      {/* Quick Test Presets Pill Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="text-zinc-400 flex items-center gap-1.5 font-bold uppercase tracking-wider">
            <Sparkles className="size-3.5 text-indigo-400" />
            Quick Test Presets
          </span>
          <span className="text-zinc-500 text-[11px]">
            Instant test vectors with known ground truth
          </span>
        </div>

        <div className="flex flex-wrap gap-2">
          {SAMPLE_ARTICLES.map((preset) => {
            const isSelected = selectedPresetId === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                onClick={() => handleApplyPreset(preset)}
                className={`px-3 py-1.5 rounded-xl font-mono text-xs border transition-all duration-200 flex items-center gap-2 ${
                  isSelected
                    ? "bg-indigo-600/30 border-indigo-400 text-white shadow-[0_0_15px_rgba(99,102,241,0.3)]"
                    : "bg-zinc-900/80 border-white/10 text-zinc-300 hover:border-white/25 hover:bg-zinc-800"
                }`}
              >
                <span
                  className={`w-2 h-2 rounded-full ${
                    preset.expectedVerdict === "REAL" ? "bg-emerald-400" : "bg-rose-400"
                  }`}
                />
                <span className="font-semibold">{preset.name}</span>
                <Badge
                  variant="outline"
                  className="text-[9px] py-0 px-1 border-white/10 text-zinc-400 uppercase"
                >
                  {preset.category}
                </Badge>
              </button>
            );
          })}
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Optional Headline Input */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="article-title" className="text-xs font-mono text-zinc-300">
              Headline or Reference Title (Optional)
            </Label>
            <span className="text-[10px] font-mono text-zinc-500">{titleValue.length}/300</span>
          </div>
          <Input
            id="article-title"
            placeholder="e.g. Breaking: Federal Reserve Adjusts Interbank Swap Facilities"
            {...register("title")}
            disabled={isLoading}
            className="bg-zinc-950/60 border-white/10 text-white font-mono text-sm placeholder:text-zinc-600 focus-visible:ring-indigo-500 focus-visible:border-indigo-500"
          />
          {errors.title && (
            <p className="text-xs text-rose-400 font-mono flex items-center gap-1 mt-1">
              <AlertCircle className="size-3" />
              {errors.title.message}
            </p>
          )}
        </div>

        {/* Article Body Textarea */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="article-text" className="text-xs font-mono text-zinc-300">
              Article Text Body <span className="text-rose-400">*</span>
            </Label>
            <div className="flex items-center gap-3 text-[11px] font-mono text-zinc-400">
              <span>{wordCount} words</span>
              <span>•</span>
              <span>{charCount} characters</span>
            </div>
          </div>

          <Textarea
            id="article-text"
            rows={7}
            placeholder="Paste complete news article, press release, or statement text here for dual-model veracity evaluation and token attention saliency mapping..."
            {...register("text")}
            disabled={isLoading}
            className="bg-zinc-950/80 border-white/10 text-white font-mono text-xs md:text-sm placeholder:text-zinc-600 leading-relaxed focus-visible:ring-indigo-500 focus-visible:border-indigo-500 resize-y min-h-[160px]"
          />
          {errors.text && (
            <p className="text-xs text-rose-400 font-mono flex items-center gap-1 mt-1">
              <AlertCircle className="size-3" />
              {errors.text.message}
            </p>
          )}
        </div>

        {/* Action Toolbar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 pt-2 border-t border-white/5">
          {/* Model Selection Tabs */}
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider block">
              Inference Mode
            </span>
            <Tabs
              value={targetModel}
              onValueChange={(val) => setValue("targetModel", val as ModelTarget)}
              className="w-full sm:w-auto"
            >
              <TabsList className="bg-zinc-900 border border-white/10 p-1">
                <TabsTrigger value="both" className="text-xs font-mono">
                  Dual-Model (LSTM + BERT)
                </TabsTrigger>
                <TabsTrigger value="bert" className="text-xs font-mono">
                  BERT Transformer
                </TabsTrigger>
                <TabsTrigger value="lstm" className="text-xs font-mono">
                  Bi-LSTM Recurrent
                </TabsTrigger>
              </TabsList>
              <TabsContent value="both" className="hidden" />
              <TabsContent value="bert" className="hidden" />
              <TabsContent value="lstm" className="hidden" />
            </Tabs>
          </div>

          {/* Buttons */}
          <div className="flex items-center gap-2 self-end sm:self-auto pt-2 sm:pt-0">
            <button
              type="button"
              onClick={handleCleanPaste}
              disabled={isLoading}
              title="Paste cleaned text from clipboard"
              className="p-2.5 rounded-xl border border-white/10 bg-zinc-900/60 text-zinc-400 hover:text-white hover:border-white/20 transition-colors cursor-pointer"
            >
              <ClipboardCheck className="size-4" />
            </button>
            <button
              type="button"
              onClick={handleClear}
              disabled={isLoading || (!textValue && !titleValue)}
              title="Clear input"
              className="p-2.5 rounded-xl border border-white/10 bg-zinc-900/60 text-zinc-400 hover:text-rose-400 hover:border-rose-500/30 transition-colors disabled:opacity-40 disabled:pointer-events-none cursor-pointer"
            >
              <Eraser className="size-4" />
            </button>

            <PredictButton
              isLoading={isLoading}
              loadingStep={loadingStep}
              disabled={!textValue.trim() || isLoading}
            />
          </div>
        </div>
      </form>
    </div>
  );
}
