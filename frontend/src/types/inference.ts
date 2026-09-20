import type { TokenSaliency } from "@/components/react-bits/TokenHighlighter";

export type ModelTarget = "lstm" | "bert" | "both";

export type VeracityVerdict = "REAL" | "FAKE" | "UNCERTAIN";

export interface SingleModelResult {
  modelId: "lstm" | "bert";
  modelName: string;
  verdict: VeracityVerdict;
  confidence: number; // 0.00 - 1.00
  probabilityFake: number;
  probabilityReal: number;
  latencyMs: number;
  tokensCount: number;
  paramCount: string;
  architecture: string;
  saliencyTokens: TokenSaliency[];
}

export interface DualModelComparisonResult {
  id: string;
  timestamp: string;
  title: string;
  text: string;
  targetModel: ModelTarget;
  lstm?: SingleModelResult;
  bert?: SingleModelResult;
  consensus?: "AGREEMENT" | "DIVERGENCE";
  differentialConfidence?: number;
  isSimulated: boolean;
  simulationNotice?: string;
}

export interface ArticlePreset {
  id: string;
  name: string;
  category: "satire" | "credible" | "clickbait" | "conspiracy";
  title: string;
  text: string;
  expectedVerdict: VeracityVerdict;
  description: string;
}

export interface BenchmarkMetrics {
  name: string;
  family: string;
  tag: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  rocAuc: number;
  brierScore: number;
  latencyMs: number;
  modelSizeMb: number;
  paramCount: string;
  ramMb: number;
  interpretability: string;
  operationalRisk: string;
  isChampion: boolean;
  confusionMatrix: {
    tp: number;
    fp: number;
    tn: number;
    fn: number;
  };
  rocCurve: Array<{ fpr: number; tpr: number }>;
}

export interface ArchitectureDetail {
  layer: string;
  lstmConfig: string;
  bertConfig: string;
  rationale: string;
}
