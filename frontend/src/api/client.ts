import axios from 'axios';
import { storage } from '../utils/storage';
import { useAuthStore } from '../store/useAuthStore';

// Change to LAN IP when testing on physical device, or 10.0.2.2 for Android Emulator
export const API_URL = 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(async (config) => {
  const token = await storage.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Trigger refresh logic on 401
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await storage.getRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const { data } = await axios.post(`${API_URL}/auth/refresh/`, {
          refresh: refreshToken,
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
        await storage.clearTokens();
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
