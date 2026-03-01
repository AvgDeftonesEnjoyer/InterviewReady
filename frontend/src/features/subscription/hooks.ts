import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';

export interface SubscriptionStatus {
    plan: 'FREE' | 'PRO' | 'PRO_PLUS';
    is_active: boolean;
    started_at: string | null;
    expires_at: string | null;
    billing_cycle: 'monthly' | 'annual';
    price: number;
    interviews_remaining: number;
    interviews_limit: number;
}

export const useSubscription = () => {
    return useQuery<SubscriptionStatus>({
        queryKey: ['subscription-status'],
        queryFn: async () => {
            // ✅ CORRECT: Use /api/subscriptions/status/ endpoint
            const { data } = await apiClient.get('/api/subscriptions/status/');
            return data;
        },
    });
};

// Mock payment functions
export const initiateStripePayment = async () => {
    // 1. Fetch Payment Intent from backend
    // 2. Open Stripe Payment Sheet (via @stripe/stripe-react-native)
    // 3. Confirm payment on backend validation endpoint
    return Promise.resolve({ success: true, method: 'STRIPE' });
};

export const initiateApplePayment = async () => {
    // 1. Request purchase via react-native-iap
    // 2. Send receipt to backend validation endpoint
    return Promise.resolve({ success: true, method: 'APPLE' });
};
