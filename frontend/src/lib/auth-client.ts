"use client";

import { useState, useEffect, useCallback } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
export interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  locale: string;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface Session {
  user: User | null;
}

export interface SessionInfo {
  id: number;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string;
  expires_at: string;
  last_activity_at: string;
  is_current: boolean;
}

// In-memory cache
let cachedSession: Session = { user: null };
let isInitialized = false;
const listeners = new Set<() => void>();

function notifyListeners() {
  listeners.forEach((listener) => listener());
}

// API helpers
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<{ data: T | null; error: string | null }> {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      credentials: "include", // Include cookies
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      
      // Handle Pydantic validation errors (array format)
      if (Array.isArray(error)) {
        const messages = error.map((e: any) => e.msg || e.message || "Validation error").join(", ");
        return { data: null, error: messages };
      }
      
      // Handle standard error format
      const errorMessage = typeof error.detail === "string" 
        ? error.detail 
        : Array.isArray(error.detail)
          ? error.detail.map((e: any) => e.msg || e.message || "Error").join(", ")
          : "Request failed";
      
      return { data: null, error: errorMessage };
    }

    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    return { data: null, error: "Network error" };
  }
}

// Session hook
export function useSession() {
  const [data, setData] = useState<Session>(cachedSession);
  const [isPending, setIsPending] = useState(!isInitialized);

  const refresh = useCallback(async () => {
    const { data: authStatus } = await fetchAPI<{ authenticated: boolean; user: User | null }>(
      "/api/v1/auth/me"
    );

    if (authStatus?.authenticated && authStatus.user) {
      cachedSession = { user: authStatus.user };
    } else {
      cachedSession = { user: null };
    }

    isInitialized = true;
    setData({ ...cachedSession });
    setIsPending(false);
    notifyListeners();
  }, []);

  useEffect(() => {
    // Initial load
    if (!isInitialized) {
      refresh();
    }

    // Subscribe to changes
    const listener = () => setData({ ...cachedSession });
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }, [refresh]);

  return { data, isPending, refresh };
}

// Sign in
export const signIn = {
  email: async ({
    email,
    password,
  }: {
    email: string;
    password: string;
  }): Promise<{ data: Session | null; error: { message: string } | null }> => {
    const { data, error } = await fetchAPI<{ token: string; user: User; expires_at: string }>(
      "/api/v1/auth/login",
      {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }
    );

    if (error) {
      return { data: null, error: { message: error } };
    }

    if (data?.user) {
      cachedSession = { user: data.user };
      isInitialized = true;
      notifyListeners();
      return { data: cachedSession, error: null };
    }

    return { data: null, error: { message: "Login failed" } };
  },

  social: async ({
    provider,
    callbackURL,
  }: {
    provider: string;
    callbackURL: string;
  }): Promise<void> => {
    // Social login not implemented in backend yet
    // For now, show message
    alert(`Social login (${provider}) coming soon!`);
  },
};

// Sign up
export const signUp = {
  email: async ({
    email,
    password,
    name,
  }: {
    email: string;
    password: string;
    name: string;
  }): Promise<{ data: User | null; error: { message: string } | null }> => {
    const { data, error } = await fetchAPI<User>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, name, locale: "sk" }),
    });

    if (error) {
      return { data: null, error: { message: error } };
    }

    return { data, error: null };
  },
};

// Sign out
export const signOut = async (): Promise<void> => {
  await fetchAPI("/api/v1/auth/logout", { method: "POST" });
  cachedSession = { user: null };
  isInitialized = true;
  notifyListeners();
};

// Get current session (for SSR)
export const getSession = (): Session => cachedSession;

// Password change
export const changePassword = async (
  oldPassword: string,
  newPassword: string
): Promise<{ success: boolean; error: string | null }> => {
  const { data, error } = await fetchAPI<{ message: string }>("/api/v1/auth/password/change", {
    method: "POST",
    body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
  });

  return { success: !error, error };
};

// Get all sessions
export const getSessions = async (): Promise<{
  sessions: SessionInfo[];
  error: string | null;
}> => {
  const { data, error } = await fetchAPI<{ sessions: SessionInfo[]; total: number }>(
    "/api/v1/auth/sessions"
  );

  return { sessions: data?.sessions || [], error };
};

// Revoke session
export const revokeSession = async (
  sessionId: number
): Promise<{ success: boolean; error: string | null }> => {
  const { error } = await fetchAPI(`/api/v1/auth/sessions/${sessionId}/revoke`, {
    method: "POST",
  });

  return { success: !error, error };
};

// Revoke all sessions (logout everywhere)
export const revokeAllSessions = async (): Promise<{
  success: boolean;
  error: string | null;
}> => {
  const { error } = await fetchAPI("/api/v1/auth/sessions/revoke-all", {
    method: "POST",
  });

  if (!error) {
    cachedSession = { user: null };
    notifyListeners();
  }

  return { success: !error, error };
};
