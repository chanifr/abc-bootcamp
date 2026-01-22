/**
 * Authentication API Service
 */

import { apiFormRequest, apiRequest } from './client';
import { API_ENDPOINTS } from './config';
import { storeTokens, clearTokens, type AuthTokens, type User } from './auth';

export interface LoginCredentials {
  username: string;
  password: string;
}

/**
 * Login with username and password
 */
export async function login(credentials: LoginCredentials): Promise<AuthTokens> {
  const formData: Record<string, string> = {
    username: credentials.username,
    password: credentials.password,
  };
  const tokens = await apiFormRequest<AuthTokens>(
    API_ENDPOINTS.AUTH.LOGIN,
    formData
  );

  storeTokens(tokens);
  return tokens;
}

/**
 * Logout and clear tokens
 */
export function logout(): void {
  clearTokens();
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<User> {
  return apiRequest<User>(API_ENDPOINTS.AUTH.ME);
}

/**
 * Refresh access token
 */
export async function refreshToken(refreshToken: string): Promise<AuthTokens> {
  const tokens = await apiRequest<AuthTokens>(API_ENDPOINTS.AUTH.REFRESH, {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  storeTokens(tokens);
  return tokens;
}
