"use client";

import { create } from "zustand";
import { api } from "@/lib/api";
import type { User } from "@/types/api";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    full_name?: string;
    company_name?: string;
  }) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  login: async (email, password) => {
    const data = await api.auth.login(email, password);
    localStorage.setItem("token", data.access_token);
    const user = (await api.auth.me()) as User;
    set({ user });
  },
  register: async (data) => {
    await api.auth.register(data);
    const tokenData = await api.auth.login(data.email, data.password);
    localStorage.setItem("token", tokenData.access_token);
    const user = (await api.auth.me()) as User;
    set({ user });
  },
  logout: () => {
    localStorage.removeItem("token");
    set({ user: null });
    window.location.href = "/login";
  },
  checkAuth: async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      set({ isLoading: false });
      return;
    }
    try {
      const user = (await api.auth.me()) as User;
      set({ user, isLoading: false });
    } catch {
      localStorage.removeItem("token");
      set({ user: null, isLoading: false });
    }
  },
}));
