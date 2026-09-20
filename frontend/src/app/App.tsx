import confetti from "canvas-confetti";
import {
  BarChart3,
  BrainCircuit,
  Cpu,
  Github,
  History,
  Info,
  Layers,
  Sparkles,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { AuroraBackground } from "@/components/react-bits/AuroraBackground";
import { BenchmarksHub } from "@/features/benchmarks/components/BenchmarksHub";
import { ComparisonGrid } from "@/features/comparison/components/ComparisonGrid";
import { TokenHeatmap } from "@/features/explainability/components/TokenHeatmap";
import { HistoryTable } from "@/features/history/components/HistoryTable";
import { useHistoryStore } from "@/features/history/store/historyStore";
import { useInferenceMutation } from "@/features/inference/api/useInferenceMutation";
import { type InferenceFormValues, InputArea } from "@/features/inference/components/InputArea";
import { SAMPLE_ARTICLES } from "@/features/inference/data/sampleArticles";
import type { DualModelComparisonResult } from "@/types/inference";

type ActiveTab = "inference" | "explainability" | "benchmarks" | "history";

export function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("inference");
  const [loadingStep, setLoadingStep] = useState<string>("Tokenizing sequence...");
  const [currentResult, setCurrentResult] = useState<DualModelComparisonResult | null>(null);

  const { addRecord } = useHistoryStore();
  const inferenceMutation = useInferenceMutation();
  const isLoading = inferenceMutation.isPending;

  const handleRunInference = async (values: InferenceFormValues) => {
    setLoadingStep("1/3 Subword tokenization & embedding mapping...");

    const step1Timer = setTimeout(() => {
      setLoadingStep("2/3 Vectorizing bidirectional representations...");
    }, 400);

    const step2Timer = setTimeout(() => {
      setLoadingStep("3/3 Computing cross-attention & sequence logits...");
    }, 900);

    try {
      const result = await inferenceMutation.mutateAsync(values);
      clearTimeout(step1Timer);
      clearTimeout(step2Timer);

      setCurrentResult(result);
      addRecord(result);

      if (result.bert?.verdict === "REAL" || result.lstm?.verdict === "REAL") {
        confetti({
          particleCount: 50,
          spread: 60,
          origin: { y: 0.8 },
          colors: ["#34d399", "#818cf8", "#60a5fa"],
        });
      }

      toast.success("Analysis completed successfully", {
        description: `Verdict: ${result.bert?.verdict ?? result.lstm?.verdict} with consensus: ${result.consensus ?? "Single"}`,
      });
    } catch (_err) {
      clearTimeout(step1Timer);
      clearTimeout(step2Timer);
      toast.error("Inference execution error", {
        description: "Falling back to simulated classification engine.",
      });
    }
  };

  const handleSelectFromHistory = (item: DualModelComparisonResult) => {
    setCurrentResult(item);
    setActiveTab("inference");
    toast.info("Audit record loaded", {
      description: `Loaded "${item.title || "Untitled Article"}" from local audit trail.`,
    });
  };

  return (
    <AuroraBackground>
      <div className="min-h-screen flex flex-col justify-between text-zinc-100 max-w-7xl mx-auto px-4 py-6 md:px-8 space-y-8">
        {/* Navigation & Header */}
        <header className="space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="size-11 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center glow-indigo">
                <BrainCircuit className="size-6 text-indigo-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl md:text-2xl font-black font-mono tracking-tight text-white">
                    VERITAS AI
                  </h1>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 font-bold">
                    v2.0 Production
                  </span>
                </div>
                <p className="text-xs text-zinc-400 font-mono">
                  Dual-Model Fake News Detection & Token Saliency Architecture
                </p>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-zinc-900/80 border border-white/10 text-xs font-mono">
              <button
                type="button"
                onClick={() => setActiveTab("inference")}
                className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                  activeTab === "inference"
                    ? "bg-indigo-600 text-white shadow-md font-bold"
                    : "text-zinc-400 hover:text-white hover:bg-white/5"
                }`}
              >
                <Cpu className="size-3.5" />
                Inference Studio
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("explainability")}
                className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                  activeTab === "explainability"
                    ? "bg-indigo-600 text-white shadow-md font-bold"
                    : "text-zinc-400 hover:text-white hover:bg-white/5"
                }`}
              >
                <Sparkles className="size-3.5" />
                Explainability Lab
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("benchmarks")}
                className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                  activeTab === "benchmarks"
                    ? "bg-indigo-600 text-white shadow-md font-bold"
                    : "text-zinc-400 hover:text-white hover:bg-white/5"
                }`}
              >
                <BarChart3 className="size-3.5" />
                Benchmarks Hub
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("history")}
                className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${
                  activeTab === "history"
                    ? "bg-indigo-600 text-white shadow-md font-bold"
                    : "text-zinc-400 hover:text-white hover:bg-white/5"
                }`}
              >
                <History className="size-3.5" />
                Audit Trail
              </button>

              <a
                href="https://github.com/tejaswin-amara/Fake-News-Detection-Using-NLP-LSTM-and-BERT-Transformer-Models"
                target="_blank"
                rel="noreferrer"
                title="View GitHub Repository"
                className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/5 transition-colors ml-1"
              >
                <Github className="size-4" />
              </a>
            </nav>
          </div>

          {/* Simulation Fallback Banner */}
          {currentResult?.isSimulated && (
            <div className="px-4 py-2 rounded-xl bg-indigo-950/40 border border-indigo-500/20 text-indigo-300 text-xs font-mono flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Info className="size-4 shrink-0 text-indigo-400" />
                <span>
                  <strong>Running in Local Demo / Simulation Mode:</strong> Deterministic subword
                  tokenizer and attention saliency engine active. Full backend endpoints
                  (/api/predict/lstm, /api/predict/bert) will auto-connect when Python server is
                  online.
                </span>
              </div>
              <span className="text-[10px] text-zinc-400 shrink-0 hidden sm:inline">
                Zero Cloud Dependencies
              </span>
            </div>
          )}
        </header>

        {/* Main Content Area */}
        <main className="space-y-8">
          {activeTab === "inference" && (
            <div className="space-y-8">
              {/* Input Area Form */}
              <section aria-label="Inference Form">
                <InputArea
                  onSubmit={handleRunInference}
                  isLoading={isLoading}
                  loadingStep={loadingStep}
                  initialValues={
                    currentResult
                      ? {
                          title: currentResult.title,
                          text: currentResult.text,
                          targetModel: currentResult.targetModel,
                        }
                      : {
                          title: SAMPLE_ARTICLES[0]?.title,
                          text: SAMPLE_ARTICLES[0]?.text,
                          targetModel: "both",
                        }
                  }
                />
              </section>

              {/* Dual Model Comparison Cards */}
              <section aria-label="Model Predictions">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-bold font-mono tracking-tight text-white flex items-center gap-2">
                    <Layers className="size-4 text-indigo-400" />
                    {currentResult?.targetModel === "bert"
                      ? "FINE-TUNED BERT TRANSFORMER INFERENCE"
                      : currentResult?.targetModel === "lstm"
                        ? "GLOVE + BI-LSTM RECURRENT INFERENCE"
                        : "DUAL-MODEL INFERENCE & ARCHITECTURAL COMPARISON"}
                  </h2>
                </div>

                <ComparisonGrid lstm={currentResult?.lstm} bert={currentResult?.bert} />
              </section>

              {/* Saliency Heatmap Preview */}
              {currentResult && (
                <section aria-label="Attention Heatmap Preview">
                  <TokenHeatmap lstm={currentResult.lstm} bert={currentResult.bert} />
                </section>
              )}
            </div>
          )}

          {activeTab === "explainability" && (
            <section aria-label="Explainability Lab" className="space-y-6">
              {currentResult ? (
                <TokenHeatmap lstm={currentResult.lstm} bert={currentResult.bert} />
              ) : (
                <div className="glass-panel p-10 rounded-2xl border border-white/10 text-center space-y-4">
                  <Sparkles className="size-8 text-indigo-400 mx-auto animate-pulse" />
                  <h3 className="text-lg font-mono font-bold text-white">
                    NO INFERENCE EXECUTED YET
                  </h3>
                  <p className="text-xs text-zinc-400 max-w-md mx-auto">
                    Please submit an article in the Inference Studio to generate live multi-head
                    cross-attention tokens and bidirectional gradient heatmaps.
                  </p>
                  <button
                    type="button"
                    onClick={() => setActiveTab("inference")}
                    className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-mono font-bold uppercase transition-all cursor-pointer"
                  >
                    Go to Inference Studio
                  </button>
                </div>
              )}
            </section>
          )}

          {activeTab === "benchmarks" && (
            <section aria-label="Benchmarks Hub">
              <BenchmarksHub />
            </section>
          )}

          {activeTab === "history" && (
            <section aria-label="Audit Trail">
              <HistoryTable onSelectRecord={handleSelectFromHistory} />
            </section>
          )}
        </main>

        {/* Footer */}
        <footer className="pt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-zinc-500">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>VERITAS Neural Verification Architecture</span>
            <span>•</span>
            <span>Bi-LSTM & Fine-Tuned BERT Transformer</span>
          </div>
          <div className="flex items-center gap-4">
            <span>Geist/Inter Sans</span>
            <span>•</span>
            <span>JetBrains Mono</span>
            <span>•</span>
            <span>Radix UI + Motion</span>
          </div>
        </footer>
      </div>
    </AuroraBackground>
  );
}

export default App;
