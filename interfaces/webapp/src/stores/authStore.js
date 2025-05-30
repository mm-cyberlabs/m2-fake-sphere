import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../services/api';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      isAuthenticated: false,
      user: null,
      token: null,
      loading: false,
      error: null,

      // Actions
      login: async (credentials) => {
        set({ loading: true, error: null });
        try {
          const response = await authAPI.login(credentials);
          const { token, user } = response.data;
          
          localStorage.setItem('authToken', token);
          set({
            isAuthenticated: true,
            user,
            token,
            loading: false,
            error: null
          });
          
          return { success: true };
        } catch (error) {
          const errorMessage = error.response?.data?.error || 'Login failed';
          set({ loading: false, error: errorMessage });
          return { success: false, error: errorMessage };
        }
      },

      logout: async () => {
        try {
          await authAPI.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          localStorage.removeItem('authToken');
          set({
            isAuthenticated: false,
            user: null,
            token: null,
            loading: false,
            error: null
          });
        }
      },

      verifyToken: async () => {
        const token = localStorage.getItem('authToken');
        if (!token) {
          set({ isAuthenticated: false, user: null, token: null });
          return false;
        }

        try {
          const response = await authAPI.verify();
          const { user } = response.data;
          
          set({
            isAuthenticated: true,
            user,
            token,
            error: null
          });
          
          return true;
        } catch (error) {
          localStorage.removeItem('authToken');
          set({
            isAuthenticated: false,
            user: null,
            token: null,
            error: 'Token verification failed'
          });
          return false;
        }
      },

      refreshToken: async () => {
        try {
          const response = await authAPI.refresh();
          const { token } = response.data;
          
          localStorage.setItem('authToken', token);
          set({ token });
          
          return true;
        } catch (error) {
          console.error('Token refresh failed:', error);
          get().logout();
          return false;
        }
      },

      clearError: () => set({ error: null }),

      // Initialize auth state
      initialize: async () => {
        const token = localStorage.getItem('authToken');
        if (token) {
          await get().verifyToken();
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        token: state.token,
      }),
    }
  )
);