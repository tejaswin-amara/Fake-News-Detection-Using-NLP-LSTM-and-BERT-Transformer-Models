import { z } from "zod";

export * from "@/types/inference";

export const predictRequestSchema = z.object({
  title: z.string().max(300, "Title cannot exceed 300 characters").optional().default(""),
  text: z
    .string()
    .min(10, "Article content must be at least 10 characters long")
    .max(50000, "Article content cannot exceed 50,000 characters"),
  model: z.enum(["lstm", "bert", "both"]).default("both"),
});

export type PredictRequestInput = z.infer<typeof predictRequestSchema>;

export interface PredictApiResponse {
  id?: string;
  label?: string;
  verdict?: "REAL" | "FAKE" | "UNCERTAIN";
  confidence?: number;
  probabilityReal?: number;
  probabilityFake?: number;
  lstm?: import("@/types/inference").SingleModelResult;
  bert?: import("@/types/inference").SingleModelResult;
  consensus?: "AGREEMENT" | "DIVERGENCE";
  differentialConfidence?: number;
  latencyMs?: number;
}
