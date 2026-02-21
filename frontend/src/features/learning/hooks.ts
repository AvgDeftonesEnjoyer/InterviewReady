import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '../../api/client';

export interface AnswerOption {
    id: number;
    text: string;
}

export interface Question {
    id: number;
    category: string;
    difficulty: string;
    language: string;
    text: string;
    options: AnswerOption[];
}

export const useDailyQuestions = () => {
    return useQuery<Question[]>({
        queryKey: ['daily-questions'],
        queryFn: async () => {
            const { data } = await apiClient.get('/learning/daily/');
            return data;
        },
    });
};

export const useSubmitAnswer = () => {
    return useMutation({
        mutationFn: async ({ questionId, optionId }: { questionId: number; optionId: number }) => {
            const { data } = await apiClient.post('/learning/submit/', {
                question_id: questionId,
                option_id: optionId
            });
            return data as { is_correct: boolean; explanation: string; xp_earned: number };
        }
    });
};
