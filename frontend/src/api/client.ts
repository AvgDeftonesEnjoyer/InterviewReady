import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { storage } from '../utils/storage';
import { useAuthStore } from '../store/useAuthStore';
import NetInfo from '@react-native-community/netinfo';

// Local dev API URL
// For physical device via Expo Go: set EXPO_PUBLIC_API_URL to your Mac's local IP, e.g. http://192.168.3.155:8000
// For web/simulator: http://localhost:8000 works fine
export const API_URL = process.env.EXPO_PUBLIC_API_URL ?? (__DEV__ ? 'http://localhost:8000' : 'https://your-production-api.com');

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Network status check
let isOnline = true;

// Listen to network status changes
NetInfo.addEventListener(state => {
  isOnline = state.isConnected ?? false;
  if (__DEV__) console.log('Network status changed:', isOnline ? 'online' : 'offline');
});

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Helper function for delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Retry logic with exponential backoff
const shouldRetry = (error: AxiosError): boolean => {
  if (!error.config) return false;
  
  const retryCount = (error.config as any).__retryCount || 0;
  if (retryCount >= MAX_RETRIES) return false;
  
  // Only retry on 5xx errors, network errors, or timeouts
  const status = error.response?.status;
  if (status && status >= 500 && status < 600) return true;
  if (error.code === 'ECONNABORTED') return true; // Timeout
  if (error.code === 'NETWORK_ERROR') return true;
  
  return false;
};

apiClient.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  // Check if online before making request
  if (!isOnline) {
    console.warn('API request attempted while offline:', config.url);
    // Still allow the request to go through - axios will handle the network error
  }

  // Don't add Authorization header to public endpoints
  const publicEndpoints = ['/auth/register/', '/auth/login/', '/auth/refresh/', '/auth/google/', '/auth/apple/'];
  const isPublicEndpoint = publicEndpoints.some(endpoint => config.url?.includes(endpoint));
  
  if (!isPublicEndpoint) {
    const token = await storage.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      if (__DEV__) console.log('[API] Added auth token to:', config.url);
    } else {
      if (__DEV__) console.log('[API] No token found for:', config.url);
    }
  } else {
    if (__DEV__) console.log('[API] Skipping auth for public endpoint:', config.url);
  }
  
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean; __retryCount?: number };
    
    // Check if we should retry
    if (shouldRetry(error) && !originalRequest.__retryCount) {
      originalRequest.__retryCount = 0;
    }
    
    // Retry logic for server errors and network issues
    if (originalRequest.__retryCount !== undefined && originalRequest.__retryCount < MAX_RETRIES) {
      if (shouldRetry(error)) {
        originalRequest.__retryCount += 1;
        const retryDelay = RETRY_DELAY * Math.pow(2, originalRequest.__retryCount - 1); // Exponential backoff
        
        if (__DEV__) console.log(`Retrying request (${originalRequest.__retryCount}/${MAX_RETRIES}) after ${retryDelay}ms...`);
        await delay(retryDelay);
        
        return apiClient(originalRequest);
      }
    }

    // Trigger refresh logic on 401
    const publicEndpoints = ['/auth/login/', '/auth/register/', '/auth/google/', '/auth/apple/'];
    const isPublicEndpoint = publicEndpoints.some(endpoint => originalRequest.url?.includes(endpoint));

    if (error.response?.status === 401 && !originalRequest._retry && !isPublicEndpoint) {
      originalRequest._retry = true;

      try {
        const refreshToken = await storage.getRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const { data } = await axios.post(`${API_URL}/auth/refresh/`, {
          refresh: refreshToken,
        }, {
          timeout: 10000,
        });

        // Store new tokens
        await storage.setAccessToken(data.access);
        if (data.refresh) {
          await storage.setRefreshToken(data.refresh);
        }

        apiClient.defaults.headers.common['Authorization'] = `Bearer ${data.access}`;
        originalRequest.headers['Authorization'] = `Bearer ${data.access}`;

        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        if (__DEV__) console.error('Token refresh failed, logging out user');
        await storage.clearTokens();
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }

    // Add network error information
    if (!error.response && (error.code === 'ERR_NETWORK' || error.message === 'Network Error')) {
      error.message = 'No internet connection. Please check your network and try again.';
    } else if (!error.response && error.code === 'ECONNABORTED') {
      error.message = 'Request timeout. The server took too long to respond.';
    }

    return Promise.reject(error);
  }
);

// Export network status checker
export const checkNetworkStatus = async (): Promise<boolean> => {
  const state = await NetInfo.fetch();
  isOnline = state.isConnected ?? false;
  return isOnline;
};

// Export online status
export const getOnlineStatus = (): boolean => isOnline;

export const apiService = {
  fetchDashboard: () => apiClient.get('/api/home/dashboard/'),
  startTopic: (topicId: number) => apiClient.post(`/api/home/start-topic/${topicId}/`),

  incrementDailyChallenge: async (challengeId: number, incrementAmount: number = 1) => {
    try {
      const resp = await apiClient.post(`/api/home/challenges/${challengeId}/progress/`, {
        increment: incrementAmount
      });
      return resp.data;
    } catch (e) {
      console.warn("Failed incrementing challenge progress", e);
      return null;
    }
  },
  
  // New method to check network before API calls
  checkConnection: async (): Promise<boolean> => {
    return checkNetworkStatus();
  }
};
