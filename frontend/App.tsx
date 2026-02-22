import React, { useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RootNavigator } from './src/navigation';
import { useAuthStore } from './src/store/useAuthStore';
import { storage } from './src/utils/storage';
import { Toaster } from 'react-hot-toast';
import { initI18n } from './src/i18n';

const queryClient = new QueryClient();

export default function App() {
  const { setUser, setLoading, isLoading } = useAuthStore();
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
          // Verify token or decode it (Mocking success for pure UI setup)
          setUser({ id: 1, email: 'user@test.com' });
        }
      } catch (error) {
        console.error("Failed to restore session", error);
      } finally {
        setLoading(false);
      }
    };

    restoreSession();
  }, [setLoading, setUser]);

  if (isLoading || !i18nReady) return null; // Can render Splash Screen here

  return (
    <QueryClientProvider client={queryClient}>
      <RootNavigator />
      <Toaster position="top-center" reverseOrder={true} />
    </QueryClientProvider>
  );
}
