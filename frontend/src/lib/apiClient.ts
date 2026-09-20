import axios, { type AxiosInstance, type AxiosRequestConfig } from "axios";
import type { ModelTarget, SingleModelResult } from "@/types/inference";

export interface PredictPayload {
  title?: string;
  text: string;
  model?: ModelTarget;
}

export interface PredictResponse {
  label?: string;
  verdict?: "REAL" | "FAKE" | "UNCERTAIN";
  confidence?: number;
  probabilityReal?: number;
  probabilityFake?: number;
  lstm?: SingleModelResult;
  bert?: SingleModelResult;
  consensus?: "AGREEMENT" | "DIVERGENCE";
  differentialConfidence?: number;
}

const BASE_URL = typeof window !== "undefined" ? "" : "http://127.0.0.1:8000";

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 5000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Graceful response formatting for offline/fallback handling
    return Promise.reject(error);
  }
);

export async function fetchPredictLstm(
  payload: PredictPayload,
  config?: AxiosRequestConfig
): Promise<PredictResponse> {
  const res = await apiClient.post<PredictResponse>("/api/predict/lstm", payload, config);
  return res.data;
}

export async function fetchPredictBert(
  payload: PredictPayload,
  config?: AxiosRequestConfig
): Promise<PredictResponse> {
  const res = await apiClient.post<PredictResponse>("/api/predict/bert", payload, config);
  return res.data;
}

export async function fetchPredictBoth(
  payload: PredictPayload,
  config?: AxiosRequestConfig
): Promise<PredictResponse> {
  const res = await apiClient.post<PredictResponse>("/api/predict/both", payload, config);
  return res.data;
}
