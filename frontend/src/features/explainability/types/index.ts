export type AttentionDirection = "real" | "fake" | "neutral";

export interface TokenAttention {
  id?: string;
  token: string;
  weight: number; // 0.0 to 1.0 normalized saliency
  direction: AttentionDirection;
  rawScore?: number;
  reason?: string;
}

export type TokenSaliency = TokenAttention;

export interface TokenSaliencySummary {
  totalTokens: number;
  filteredTokensCount: number;
  credibleCount: number;
  deceptiveCount: number;
  neutralCount: number;
  maxWeight: number;
}
