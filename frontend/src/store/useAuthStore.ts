import { create } from 'zustand';

interface User {
  id: number;
  email: string;
  username?: string;
  is_internal_tester?: boolean;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  onboardingCompleted: boolean;
  isLoading: boolean;
  setUser: (user: User | null, onboardingCompleted?: boolean) => void;
  setOnboardingCompleted: (value: boolean) => void;
  logout: () => void;
  setLoading: (isLoading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  onboardingCompleted: false,
  isLoading: true,
  setUser: (user, onboardingCompleted = false) => set({ user, isAuthenticated: !!user, onboardingCompleted }),
  setOnboardingCompleted: (value) => set({ onboardingCompleted: value }),
  logout: () => set({ user: null, isAuthenticated: false, onboardingCompleted: false }),
  setLoading: (isLoading) => set({ isLoading })
}));
