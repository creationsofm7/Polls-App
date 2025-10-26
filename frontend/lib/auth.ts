import { apiFetch } from "./api-client";

export interface AuthUser {
  id: number;
  email: string;
  full_name?: string | null;
  is_admin: boolean;
  created_at: string;
}

export interface SignupPayload {
  email: string;
  password: string;
  full_name?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  expires_in: number;
  user: AuthUser;
}

export async function signup(payload: SignupPayload): Promise<AuthUser> {
  return apiFetch<AuthUser>("/api/users/", {
    method: "POST",
    body: payload,
  });
}

export async function login(payload: LoginPayload): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/api/users/login", {
    method: "POST",
    body: payload,
  });
}

export async function logout(token: string): Promise<void> {
  return apiFetch<void>("/api/users/logout", {
    method: "POST",
    token,
  });
}

export async function getCurrentUser(token: string): Promise<AuthUser> {
  return apiFetch<AuthUser>("/api/users/me", {
    method: "GET",
    token,
  });
}

export async function getAdminUser(token: string): Promise<AuthUser> {
  return apiFetch<AuthUser>("/api/users/admin/me", {
    method: "GET",
    token,
  });
}

export async function refreshToken(token: string): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/api/users/refresh", {
    method: "POST",
    token,
  });
}

export async function validateToken(token: string): Promise<{ valid: boolean }> {
  return apiFetch<{ valid: boolean }>("/api/users/validate-token", {
    method: "GET",
    token,
  });
}