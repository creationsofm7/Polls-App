import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AuthUser } from "@/lib/auth";

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  expiresAt: number | null;
  setAuthData: (data: {
    token: string;
    expiresIn: number;
    user: AuthUser;
  }) => void;
  clearAuth: () => void;
  isTokenExpired: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      expiresAt: null,

      setAuthData: ({ token, expiresIn, user }) => {
        const expiresAt = Date.now() + expiresIn * 1000;
        set({ token, user, expiresAt });
      },

      clearAuth: () => {
        set({ token: null, user: null, expiresAt: null });
      },

      isTokenExpired: () => {
        const { expiresAt } = get();
        if (!expiresAt) return true;
        return Date.now() >= expiresAt;
      },
    }),
    {
      name: "auth-storage",
    }
  )
);
