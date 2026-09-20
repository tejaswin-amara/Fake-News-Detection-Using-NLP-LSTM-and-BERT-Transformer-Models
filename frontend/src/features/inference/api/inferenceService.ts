import type { TokenSaliency } from "@/components/react-bits/TokenHighlighter";
import type {
  DualModelComparisonResult,
  ModelTarget,
  SingleModelResult,
  VeracityVerdict,
} from "@/types/inference";

// Dictionary of sensationalist / deceptive lexical cues
const SENSATIONAL_PATTERNS: Array<{ regex: RegExp; weight: number; reason: string }> = [
  {
    regex: /\b(shocking|shockwaves|miracle|secret|forbidden|conspiracy)\b/i,
    weight: 0.92,
    reason: "High sensationalism lexical trigger",
  },
  {
    regex: /\b(cure|cures|banned|suppressed|censored|hidden)\b/i,
    weight: 0.88,
    reason: "Suppression / miracle cure claim pattern",
  },
  {
    regex: /\b(big pharma|deep state|whistleblower|elites|corrupt elites)\b/i,
    weight: 0.85,
    reason: "Antagonistic institutional distrust trope",
  },
  {
    regex: /\b(overnight|instant|guaranteed|revolutionary|unbelievable)\b/i,
    weight: 0.78,
    reason: "Hyperbolic outcome promise",
  },
  {
    regex: /\b(leaked|unredacted|subterranean|bunker|alien|extraterrestrial)\b/i,
    weight: 0.82,
    reason: "Unverified conspiratorial claim marker",
  },
  {
    regex: /\b(doctors beg|refused to publish|before it gets deleted)\b/i,
    weight: 0.95,
    reason: "Urgency and artificial scarcity framing",
  },
  {
    regex: /\b(glow-in-the-dark|sticker|double-sided tape|novelty)\b/i,
    weight: 0.9,
    reason: "Satirical / absurd physical impossibility",
  },
];

// Dictionary of verified / objective journalistic lexical cues
const CREDIBLE_PATTERNS: Array<{ regex: RegExp; weight: number; reason: string }> = [
  {
    regex: /\b(announced|coordinated|liquidity|facility|tariffs?|corridor)\b/i,
    weight: 0.86,
    reason: "Institutional policy and economic terminology",
  },
  {
    regex: /\b(according to|joint statements?|spokesperson|officials?)\b/i,
    weight: 0.84,
    reason: "Direct institutional attribution citation",
  },
  {
    regex: /\b(federal|reserve|central|banks?|treasury|reuters|interbank)\b/i,
    weight: 0.92,
    reason: "Primary sovereign fiscal entity naming",
  },
  {
    regex: /\b(basis points|maturit(y|ies)|auctions?|interbank|clearing)\b/i,
    weight: 0.89,
    reason: "Technical quantitative financial metrics",
  },
  {
    regex: /\b(surveyed|published|monitoring|independent|regulatory)\b/i,
    weight: 0.79,
    reason: "Methodological verifiability indicators",
  },
  {
    regex: /\b(reuters|associated press|bloomberg|peer-reviewed)\b/i,
    weight: 0.88,
    reason: "Primary news agency / verified wire attribution",
  },
];

const STOPWORDS = new Set([
  "a",
  "about",
  "above",
  "after",
  "again",
  "against",
  "all",
  "am",
  "an",
  "and",
  "any",
  "are",
  "aren't",
  "as",
  "at",
  "be",
  "because",
  "been",
  "before",
  "being",
  "below",
  "between",
  "both",
  "but",
  "by",
  "can't",
  "cannot",
  "could",
  "couldn't",
  "did",
  "didn't",
  "do",
  "does",
  "doesn't",
  "doing",
  "don't",
  "down",
  "during",
  "each",
  "few",
  "for",
  "from",
  "further",
  "had",
  "hadn't",
  "has",
  "hasn't",
  "have",
  "haven't",
  "having",
  "he",
  "he'd",
  "he'll",
  "he's",
  "her",
  "here",
  "here's",
  "hers",
  "herself",
  "him",
  "himself",
  "his",
  "how",
  "how's",
  "i",
  "i'd",
  "i'll",
  "i'm",
  "i've",
  "if",
  "in",
  "into",
  "is",
  "isn't",
  "it",
  "it's",
  "its",
  "itself",
  "let's",
  "me",
  "more",
  "most",
  "mustn't",
  "my",
  "myself",
  "no",
  "nor",
  "not",
  "of",
  "off",
  "on",
  "once",
  "only",
  "or",
  "other",
  "ought",
  "our",
  "ours",
  "ourselves",
  "out",
  "over",
  "own",
  "same",
  "shan't",
  "she",
  "she'd",
  "she'll",
  "she's",
  "should",
  "shouldn't",
  "so",
  "some",
  "such",
  "than",
  "that",
  "that's",
  "the",
  "their",
  "theirs",
  "them",
  "themselves",
  "then",
  "there",
  "there's",
  "these",
  "they",
  "they'd",
  "they'll",
  "they're",
  "they've",
  "this",
  "those",
  "through",
  "to",
  "too",
  "under",
  "until",
  "up",
  "very",
  "was",
  "wasn't",
  "we",
  "we'd",
  "we'll",
  "we're",
  "we've",
  "were",
  "weren't",
  "what",
  "what's",
  "when",
  "when's",
  "where",
  "where's",
  "which",
  "while",
  "who",
  "who's",
  "whom",
  "why",
  "why's",
  "with",
  "won't",
  "would",
  "wouldn't",
  "you",
  "you'd",
  "you'll",
  "you're",
  "you've",
  "your",
  "yours",
  "yourself",
  "yourselves",
]);

export function tokenizeAndCalculateAttention(
  text: string,
  modelType: "lstm" | "bert"
): TokenSaliency[] {
  const words = text.split(/\s+/).filter(Boolean);
  const _totalWords = words.length;

  return words.map((rawToken, index) => {
    const cleanWord = rawToken.replace(/[^a-zA-Z0-9-]/g, "").toLowerCase();
    const isStopword = STOPWORDS.has(cleanWord);

    let weight = 0.05 + ((index * 7 + cleanWord.length * 13) % 15) / 100;
    let direction: "real" | "fake" | "neutral" = "neutral";
    let rawScore = 0.0;
    let reason = "Common syntactic token with low predictive variance.";

    // Check sensational cues
    for (const pat of SENSATIONAL_PATTERNS) {
      if (pat.regex.test(cleanWord)) {
        weight = Math.min(0.98, pat.weight + (modelType === "bert" ? 0.04 : -0.02));
        direction = "fake";
        rawScore = -weight * 1.8;
        reason = pat.reason;
        break;
      }
    }

    // Check credible cues
    if (direction === "neutral") {
      for (const pat of CREDIBLE_PATTERNS) {
        if (pat.regex.test(cleanWord)) {
          weight = Math.min(0.98, pat.weight + (modelType === "bert" ? 0.03 : -0.04));
          direction = "real";
          rawScore = weight * 1.6;
          reason = pat.reason;
          break;
        }
      }
    }

    // Transformer context attention amplification for position
    if (modelType === "bert" && !isStopword && direction === "neutral" && cleanWord.length > 4) {
      weight = Math.min(0.65, weight + 0.15);
      direction = index % 3 === 0 ? "real" : "fake";
      rawScore = direction === "real" ? 0.22 : -0.25;
      reason = "Multi-head self-attention context attribution";
    }

    return {
      id: `tok-${modelType}-${index}-${cleanWord}`,
      token: rawToken,
      weight: Number(weight.toFixed(3)),
      direction,
      rawScore: Number(rawScore.toFixed(3)),
      reason,
    };
  });
}

export function simulateInference(
  title: string,
  text: string,
  targetModel: ModelTarget
): DualModelComparisonResult {
  const combined = `${title} ${text}`.toLowerCase();
  const wordsCount = text.split(/\s+/).filter(Boolean).length;

  let fakeScore = 0;
  let realScore = 0;

  for (const p of SENSATIONAL_PATTERNS) {
    const matches = combined.match(p.regex);
    if (matches) {
      fakeScore += matches.length * p.weight * 2.5;
    }
  }

  for (const p of CREDIBLE_PATTERNS) {
    const matches = combined.match(p.regex);
    if (matches) {
      realScore += matches.length * p.weight * 2.5;
    }
  }

  // Base classification bias from evidence
  const delta = realScore - fakeScore;
  const sigmoid = 1 / (1 + Math.exp(-delta * 0.8));

  // Determine probability for BERT (higher discriminative sharpness)
  let bertProbReal = Math.min(0.995, Math.max(0.005, sigmoid + (sigmoid > 0.5 ? 0.05 : -0.05)));
  let bertProbFake = 1 - bertProbReal;

  // Bi-LSTM has slightly more uncertainty and smoother boundaries
  let lstmProbReal = Math.min(0.97, Math.max(0.03, sigmoid * 0.9 + 0.05));
  let lstmProbFake = 1 - lstmProbReal;

  // If no strong signal either way, anchor around neutral
  if (fakeScore === 0 && realScore === 0) {
    bertProbReal = 0.52;
    bertProbFake = 0.48;
    lstmProbReal = 0.54;
    lstmProbFake = 0.46;
  }

  const getVerdict = (probReal: number): VeracityVerdict => {
    if (probReal >= 0.65) return "REAL";
    if (probReal <= 0.35) return "FAKE";
    return "UNCERTAIN";
  };

  const bertVerdict = getVerdict(bertProbReal);
  const lstmVerdict = getVerdict(lstmProbReal);

  const bertConfidence = Math.max(bertProbReal, bertProbFake);
  const lstmConfidence = Math.max(lstmProbReal, lstmProbFake);

  const lstmResult: SingleModelResult = {
    modelId: "lstm",
    modelName: "GloVe + Stacked Bi-LSTM",
    verdict: lstmVerdict,
    confidence: Number(lstmConfidence.toFixed(4)),
    probabilityFake: Number(lstmProbFake.toFixed(4)),
    probabilityReal: Number(lstmProbReal.toFixed(4)),
    latencyMs: Number((16.4 + Math.random() * 8.5).toFixed(1)),
    tokensCount: wordsCount,
    paramCount: "~4.2M params",
    architecture: "Bi-LSTM 2-Layer (GloVe 300d, 128 hidden x 2, Dropout 0.3, Dense 64)",
    saliencyTokens: tokenizeAndCalculateAttention(text, "lstm"),
  };

  const bertResult: SingleModelResult = {
    modelId: "bert",
    modelName: "Fine-Tuned BERT Transformer",
    verdict: bertVerdict,
    confidence: Number(bertConfidence.toFixed(4)),
    probabilityFake: Number(bertProbFake.toFixed(4)),
    probabilityReal: Number(bertProbReal.toFixed(4)),
    latencyMs: Number((138.2 + Math.random() * 24.1).toFixed(1)),
    tokensCount: wordsCount,
    paramCount: "~109.5M params",
    architecture: "BERT-base-uncased (12-layer, 768-hidden, 12-heads, [CLS] classification)",
    saliencyTokens: tokenizeAndCalculateAttention(text, "bert"),
  };

  const consensus = bertVerdict === lstmVerdict ? "AGREEMENT" : "DIVERGENCE";
  const differentialConfidence = Number(Math.abs(bertConfidence - lstmConfidence).toFixed(4));

  return {
    id: `inf-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    timestamp: new Date().toISOString(),
    title: title.trim(),
    text: text.trim(),
    targetModel,
    lstm: targetModel === "bert" ? undefined : lstmResult,
    bert: targetModel === "lstm" ? undefined : bertResult,
    consensus: targetModel === "both" ? consensus : undefined,
    differentialConfidence: targetModel === "both" ? differentialConfidence : undefined,
    isSimulated: true,
    simulationNotice:
      "Running in Local Demo/Simulation Mode (Deterministic NLP Tokenizer & Saliency Engine)",
  };
}

export async function runInference(
  title: string,
  text: string,
  targetModel: ModelTarget = "both"
): Promise<DualModelComparisonResult> {
  const fallback = simulateInference(title, text, targetModel);

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2500);

    const endpoint =
      targetModel === "lstm"
        ? "/api/predict/lstm"
        : targetModel === "bert"
          ? "/api/predict/bert"
          : "/api/predict/both";

    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ title, text, model: targetModel }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      // If server returned structured response, map it
      if (data && (data.label || data.verdict || data.lstm || data.bert)) {
        return {
          ...fallback,
          isSimulated: false,
          simulationNotice: undefined,
          ...data,
        };
      }
    }
  } catch {
    // Gracefully proceed with deterministic fallback
  }

  return fallback;
}
