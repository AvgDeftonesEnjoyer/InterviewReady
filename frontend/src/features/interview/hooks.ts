import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';

export interface Message {
    id: number;
    role: 'USER' | 'BOT';
    text: string;
    created_at: string;
}

export interface Session {
    id: number;
    mode: 'hr' | 'tech' | 'combined';
    language: string;
    status: 'active' | 'completed';
    messages: Message[];
    question_count: number;
    question_count_target: number;
}

// DEPRECATED: Old interview start with 'type' field
// Use useStartInterview instead
export const useStartSession = () => {
    return useMutation({
        mutationFn: async (type: 'SCRIPTED' | 'AI') => {
            const { data } = await apiClient.post('/interviews/start/', { type });
            return data as Session;
        },
        enabled: false, // Disabled - use useStartInterview instead
    });
};

// ✅ CURRENT: Start interview with mode, language, question_count
export const useStartInterview = () => {
    return useMutation({
        mutationFn: async (payload: {
            mode: 'hr' | 'tech' | 'combined';
            language?: string;
            question_count?: number;
        }) => {
            const { data } = await apiClient.post('/interviews/start/', payload);
            return data;
        },
    });
};

// DEPRECATED: Old message endpoint without session_id in URL
export const useSendMessage = () => {
    return useMutation({
        mutationFn: async ({ sessionId, text }: { sessionId: number; text: string }) => {
            // ✅ CORRECT: Use /interviews/<id>/message/
            const { data } = await apiClient.post(`/interviews/${sessionId}/message/`, { content: text });
            return data as Message;
        },
    });
};

// DEPRECATED: Finish session endpoint doesn't exist
export const useFinishSession = () => {
    return useMutation({
        mutationFn: async (sessionId: number) => {
            const { data } = await apiClient.post('/interviews/finish/', { session_id: sessionId });
            return data as Session;
        },
        enabled: false, // Disabled - endpoint doesn't exist
    });
};

// ✅ CURRENT: Get interview history
export const useInterviewHistory = (sessionId: number) => {
    return useQuery<Session>({
        queryKey: ['interview-history', sessionId],
        queryFn: async () => {
            const { data } = await apiClient.get(`/interviews/${sessionId}/history/`);
            return data;
        },
        enabled: !!sessionId,
    });
};
