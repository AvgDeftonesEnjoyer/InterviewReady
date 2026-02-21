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
    type: 'SCRIPTED' | 'AI';
    status: 'ACTIVE' | 'FINISHED';
    score: number | null;
    messages: Message[];
}

export const useStartSession = () => {
    return useMutation({
        mutationFn: async (type: 'SCRIPTED' | 'AI') => {
            const { data } = await apiClient.post('/interviews/start/', { type });
            return data as Session;
        }
    });
};

export const useSendMessage = () => {
    return useMutation({
        mutationFn: async ({ sessionId, text }: { sessionId: number; text: string }) => {
            const { data } = await apiClient.post('/interviews/message/', { session_id: sessionId, text });
            return data as Message;
        }
    });
};

export const useFinishSession = () => {
    return useMutation({
        mutationFn: async (sessionId: number) => {
            const { data } = await apiClient.post('/interviews/finish/', { session_id: sessionId });
            return data as Session;
        }
    });
};
