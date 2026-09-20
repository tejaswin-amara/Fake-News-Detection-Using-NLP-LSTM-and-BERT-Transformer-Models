import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { DualModelComparisonResult } from "@/types/inference";
import type { InferenceFormValues } from "../components/InputArea";
import { runInference } from "./inferenceService";

export const INFERENCE_QUERY_KEY = ["inference"] as const;

export interface UseInferenceMutationOptions {
  onSuccess?: (data: DualModelComparisonResult, variables: InferenceFormValues) => void;
  onError?: (error: Error, variables: InferenceFormValues) => void;
}

export function useInferenceMutation(options?: UseInferenceMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation<DualModelComparisonResult, Error, InferenceFormValues>({
    mutationKey: INFERENCE_QUERY_KEY,
    mutationFn: async (values: InferenceFormValues) => {
      const result = await runInference(
        values.title || "",
        values.text,
        values.targetModel || "both"
      );
      return result;
    },
    retry: 1,
    onSuccess: (data, variables) => {
      // Cache the latest result under the inference query key
      queryClient.setQueryData([...INFERENCE_QUERY_KEY, "latest"], data);
      options?.onSuccess?.(data, variables);
    },
    onError: (error, variables) => {
      options?.onError?.(error, variables);
    },
  });
}
