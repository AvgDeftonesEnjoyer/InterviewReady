import React, { useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RootNavigator } from './src/navigation';
import { useAuthStore } from './src/store/useAuthStore';
import { storage } from './src/utils/storage';
import { apiClient } from './src/api/client';
import { Toaster } from 'react-hot-toast';
import { initI18n } from './src/i18n';

const queryClient = new QueryClient();

export default function App() {
  const { user, setUser, setLoading, setOnboardingCompleted, isLoading } = useAuthStore();
  const [i18nReady, setI18nReady] = useState(false);

  useEffect(() => {
    initI18n().then(() => setI18nReady(true));
  }, []);

  useEffect(() => {
    // Attempt to restore session on launch
    const restoreSession = async () => {
      try {
        const token = await storage.getAccessToken();
        if (token) {
          // Verify token by fetching user data from server
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          try {
            const { data } = await apiClient.get('/auth/me/');
            
            // Set user and onboarding status from server response
            setUser({
              id: data.id,
              email: data.email,
              username: data.username,
              is_internal_tester: data.is_internal_tester,
            }, data.onboarding_completed);
            
            console.log('Session restored:', {
              email: data.email,
              onboarding_completed: data.onboarding_completed
            });
          } catch (error: any) {
            const isNetworkError =
              !error.response &&
              (error.code === 'ERR_NETWORK' || error.message === 'Network Error');

            if (isNetworkError) {
              // Device is offline — keep tokens, show login screen temporarily
              // User will be restored when they regain connectivity
              console.log('Offline on startup — keeping tokens, showing login');
              setUser(null, false);
            } else {
              // Token is genuinely invalid (401 or other auth error) — clear and require login
              console.log('Token invalid, requiring login');
              await storage.clearAuth();
              setUser(null, false);
            }
          }
        }
      } catch (error) {
        console.error("Failed to restore session", error);
      } finally {
        setLoading(false);
      }
    };

    restoreSession();
  }, [setLoading, setUser, setOnboardingCompleted]);

  if (isLoading || !i18nReady) return null; // Can render Splash Screen here

  return (
    <QueryClientProvider client={queryClient}>
      <RootNavigator />
      <Toaster position="top-center" reverseOrder={true} />
    </QueryClientProvider>
  );
}
