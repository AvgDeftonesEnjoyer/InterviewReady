import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
    question_type?: 'multiple_choice' | 'true_false' | 'text';
    xp_reward?: number;
    is_answered?: boolean;
}

// DEPRECATED: Old Daily Questions API - not used anymore
// Use useTopics() instead
export const useDailyQuestions = () => {
    return useQuery<Question[]>({
        queryKey: ['daily-questions'],
        queryFn: async () => {
            const { data } = await apiClient.get('/api/learning/daily/');
            return data;
        },
        enabled: false, // Disabled by default - use useTopics instead
    });
};

// DEPRECATED: Old Submit Answer API - replaced by useSubmitLearningAnswer
export const useSubmitAnswer = () => {
    return useMutation({
        mutationFn: async ({ questionId, optionId }: { questionId: number; optionId: number }) => {
            const { data } = await apiClient.post('/api/learning/submit/', {
                question_id: questionId,
                option_id: optionId
            });
            return data as { is_correct: boolean; explanation: string; xp_earned: number };
        },
        enabled: false, // Disabled - use useSubmitLearningAnswer instead
    });
};


// --- New Learning Hooks ---

export interface Topic {
    id: number;
    name: string;
    icon: string;
    language: string;
    total_questions: number;
    completed_questions: number;
    progress_percent: number;
    is_completed: boolean;
}

export const useTopics = () => {
    return useQuery<Topic[]>({
        queryKey: ['learning-topics'],
        queryFn: async () => {
            // Note: with pagination this might be data.results or just data.
            const { data } = await apiClient.get('/api/learning/topics/');
            // Handle DRF pagination just in case
            return data.results ? data.results : data;
        }
    });
};

export const useTopicQuestions = (topicId: number) => {
    return useQuery<Question[]>({
        queryKey: ['topic-questions', topicId],
        queryFn: async () => {
            const { data } = await apiClient.get(`/api/learning/topics/${topicId}/questions/`);
            return data.results ? data.results : data;
        },
        enabled: !!topicId,
    });
};

export interface AnswerResponse {
    is_correct: boolean;
    correct_option_id: number;
    explanation: string;
    xp_earned: number;
    total_xp_today: number;
    topic_progress: number;
    previously_answered: boolean;
}

export const useSubmitLearningAnswer = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (payload: {
            question_id: number;
            answer_option_id?: number | null;
            answer_text?: string;
            session_id?: string;
        }) => {
            const { data } = await apiClient.post('/api/learning/answer/', payload);
            return data as AnswerResponse;
        },
        onSuccess: () => {
            // Invalidate to refetch progress
            queryClient.invalidateQueries({ queryKey: ['home-dashboard'] });
            queryClient.invalidateQueries({ queryKey: ['learning-topics'] });
        }
    });
};

export interface SessionSummary {
    total_answered: number;
    correct: number;
    accuracy: number;
    xp_earned: number;
}

export const useSessionSummary = (sessionId: string) => {
    return useQuery<SessionSummary>({
        queryKey: ['session-summary', sessionId],
        queryFn: async () => {
            const { data } = await apiClient.get(`/api/learning/session/summary/?session_id=${sessionId}`);
            return data;
        },
        enabled: !!sessionId,
    });
};
