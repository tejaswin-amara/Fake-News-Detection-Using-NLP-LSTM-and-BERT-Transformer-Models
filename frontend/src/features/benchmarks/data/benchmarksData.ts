import type { ArchitectureDetail, BenchmarkMetrics } from "@/types/inference";

export const BENCHMARK_MODELS: BenchmarkMetrics[] = [
  {
    name: "Fine-Tuned BERT (bert-base-uncased)",
    family: "Transformer / Pre-trained LLM",
    tag: "Highest Discriminative F1",
    accuracy: 0.892,
    precision: 0.912,
    recall: 0.841,
    f1Score: 0.875,
    rocAuc: 0.9583,
    brierScore: 0.125,
    latencyMs: 145.0,
    modelSizeMb: 420.0,
    paramCount: "109.5M",
    ramMb: 1200,
    interpretability: "Multi-Head Cross-Attention & Integrated Gradients",
    operationalRisk: "High compute latency, violates 50ms real-time SLA without GPU",
    isChampion: false,
    confusionMatrix: {
      tp: 885,
      fp: 88,
      fn: 115,
      tn: 912,
    },
    rocCurve: [
      { fpr: 0.0, tpr: 0.0 },
      { fpr: 0.02, tpr: 0.45 },
      { fpr: 0.05, tpr: 0.72 },
      { fpr: 0.08, tpr: 0.88 },
      { fpr: 0.12, tpr: 0.94 },
      { fpr: 0.2, tpr: 0.97 },
      { fpr: 0.35, tpr: 0.99 },
      { fpr: 1.0, tpr: 1.0 },
    ],
  },
  {
    name: "GloVe + Stacked BiLSTM",
    family: "Recurrent Deep Learning",
    tag: "Real-Time Sequential",
    accuracy: 0.832,
    precision: 0.844,
    recall: 0.795,
    f1Score: 0.8182,
    rocAuc: 0.8889,
    brierScore: 0.184,
    latencyMs: 18.5,
    modelSizeMb: 42.0,
    paramCount: "4.2M",
    ramMb: 350,
    interpretability: "Hidden Sequence States & Gradient Saliency",
    operationalRisk: "Moderate CPU recurrent cell execution overhead",
    isChampion: false,
    confusionMatrix: {
      tp: 820,
      fp: 156,
      fn: 180,
      tn: 844,
    },
    rocCurve: [
      { fpr: 0.0, tpr: 0.0 },
      { fpr: 0.05, tpr: 0.38 },
      { fpr: 0.1, tpr: 0.62 },
      { fpr: 0.16, tpr: 0.79 },
      { fpr: 0.25, tpr: 0.89 },
      { fpr: 0.4, tpr: 0.94 },
      { fpr: 0.6, tpr: 0.98 },
      { fpr: 1.0, tpr: 1.0 },
    ],
  },
  {
    name: "TF-IDF + Logistic Regression (L2 - Champion)",
    family: "Linear / Classical ML",
    tag: "Production Serving Champion",
    accuracy: 0.865,
    precision: 0.875,
    recall: 0.84,
    f1Score: 0.8571,
    rocAuc: 0.9444,
    brierScore: 0.1365,
    latencyMs: 0.3,
    modelSizeMb: 0.05,
    paramCount: "25,000 features",
    ramMb: 45,
    interpretability: "Direct linear sparse coefficient log-odds odds mapping",
    operationalRisk: "Minimal (deterministic CPU serving, sub-millisecond)",
    isChampion: true,
    confusionMatrix: {
      tp: 840,
      fp: 120,
      fn: 160,
      tn: 880,
    },
    rocCurve: [
      { fpr: 0.0, tpr: 0.0 },
      { fpr: 0.03, tpr: 0.48 },
      { fpr: 0.06, tpr: 0.74 },
      { fpr: 0.1, tpr: 0.88 },
      { fpr: 0.18, tpr: 0.95 },
      { fpr: 0.3, tpr: 0.98 },
      { fpr: 1.0, tpr: 1.0 },
    ],
  },
  {
    name: "TF-IDF + XGBoost",
    family: "Gradient Tree Boosting",
    tag: "High Tree Precision",
    accuracy: 0.842,
    precision: 0.852,
    recall: 0.816,
    f1Score: 0.8333,
    rocAuc: 0.9167,
    brierScore: 0.152,
    latencyMs: 1.51,
    modelSizeMb: 0.85,
    paramCount: "300 trees",
    ramMb: 95,
    interpretability: "TreeExplainer SHAP & Feature Gain",
    operationalRisk: "Low (fast CPU tree traversal)",
    isChampion: false,
    confusionMatrix: {
      tp: 816,
      fp: 142,
      fn: 184,
      tn: 858,
    },
    rocCurve: [
      { fpr: 0.0, tpr: 0.0 },
      { fpr: 0.04, tpr: 0.42 },
      { fpr: 0.08, tpr: 0.68 },
      { fpr: 0.14, tpr: 0.84 },
      { fpr: 0.22, tpr: 0.92 },
      { fpr: 1.0, tpr: 1.0 },
    ],
  },
];

export const ARCHITECTURE_DETAILS: ArchitectureDetail[] = [
  {
    layer: "Tokenization & Vocabulary",
    lstmConfig:
      "GloVe 300-dimensional pre-trained word vectors (Vocab: 40,000 tokens, Sequence length: 256)",
    bertConfig:
      "WordPiece Subword Tokenizer (Vocab: 30,522 tokens, Sequence length: 512 with [CLS]/[SEP])",
    rationale:
      "BERT resolves out-of-vocabulary terms into subword fragments, avoiding unknown token information loss.",
  },
  {
    layer: "Sequence Modeling",
    lstmConfig:
      "2-Layer Stacked Bidirectional LSTM (128 hidden units per direction, 256 merged state)",
    bertConfig:
      "12 Transformer Encoder Layers with 12 Self-Attention Heads (Hidden dim: 768, Feed-forward: 3072)",
    rationale:
      "Bi-LSTM preserves sequential recurrence with O(N) complexity; BERT achieves parallel all-to-all cross-attention.",
  },
  {
    layer: "Regularization & Dropout",
    lstmConfig:
      "Spatial Dropout 0.2 on embeddings, Recurrent Dropout 0.3 on LSTM cells, Dense Dropout 0.4",
    bertConfig:
      "Attention Dropout 0.1, Hidden Dropout 0.1, LayerNorm (eps = 1e-12), Weight Decay 0.01",
    rationale:
      "Extensive dropout prevents over-fitting on deceptive clickbait keywords and forces generalized syntax learning.",
  },
  {
    layer: "Classification Head",
    lstmConfig:
      "Global Average Pooling + Max Pooling concat -> Dense(64, ReLU) -> Dense(1, Sigmoid)",
    bertConfig: "[CLS] pooled token output -> Dropout(0.1) -> Dense(768) -> Dense(2, Softmax)",
    rationale:
      "Dual pooling captures both peak emotional signals and global discourse tone across the article body.",
  },
  {
    layer: "Inference Latency SLA",
    lstmConfig: "18.5 ms (CPU) / 3.8 ms (GPU) — Real-Time Streaming Capable",
    bertConfig: "145.0 ms (CPU) / 14.2 ms (GPU) — High-Precision Verification",
    rationale:
      "Bi-LSTM delivers sub-20ms edge classification; BERT serves as the authoritative second-pass arbiter.",
  },
];
