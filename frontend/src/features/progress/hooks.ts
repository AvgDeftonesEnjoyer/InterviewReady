import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';

export interface ProgressStats {
    current_level: number;
    total_xp: number;
    streak_days: number;
    next_level_xp: number;
    progress_percent: number;
}

export const useProgressStats = () => {
    return useQuery<ProgressStats>({
        queryKey: ['progress-stats'],
        queryFn: async () => {
            const { data } = await apiClient.get('/progress/stats/');
            return data;
        },
    });
};
