import { useMutation } from '@tanstack/react-query';
import { apiClient } from '../../api/client';

export const useEvaluateAI = () => {
    return useMutation({
        mutationFn: async ({ question, answer }: { question: string; answer: string }) => {
            const { data } = await apiClient.post('/ai/evaluate/', { question, answer });
            return data as { evaluation: string; followup: string };
        }
    });
};
