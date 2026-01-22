/**
 * API Client with authentication and error handling
 */

import { API_BASE_URL } from './config';
import { getAccessToken, clearTokens } from './auth';

export class APIError extends Error {
  public status: number;
  public statusText: string;
  public data?: any;

  constructor(
    status: number,
    statusText: string,
    data?: any
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = 'APIError';
    this.status = status;
    this.statusText = statusText;
    this.data = data;
  }
}

interface RequestOptions extends RequestInit {
  skipAuth?: boolean;
}

/**
 * Make an authenticated API request
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { skipAuth, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string> || {}),
  };

  // Add authentication token if not skipped
  if (!skipAuth) {
    const token = getAccessToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
    });

    // Handle authentication errors
    if (response.status === 401) {
      clearTokens();
      // Could trigger a redirect to login page here
      throw new APIError(401, 'Unauthorized', { message: 'Authentication required' });
    }

    // Handle other HTTP errors
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: response.statusText };
      }
      throw new APIError(response.status, response.statusText, errorData);
    }

    // Parse and return JSON response
    const data = await response.json();
    return data as T;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    // Network or other errors
    throw new Error(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Make a form-data request (for login)
 */
export async function apiFormRequest<T>(
  endpoint: string,
  formData: Record<string, string>,
  options: RequestOptions = {}
): Promise<T> {
  const body = new URLSearchParams(formData);

  return apiRequest<T>(endpoint, {
    ...options,
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: body.toString(),
    skipAuth: true,
  });
}
