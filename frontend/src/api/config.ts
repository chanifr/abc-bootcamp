/**
 * API Configuration
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const API_VERSION = '/api/v1';

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: `${API_VERSION}/auth/login`,
    REFRESH: `${API_VERSION}/auth/refresh`,
    ME: `${API_VERSION}/auth/me`,
  },
  CANDIDATES: {
    LIST: `${API_VERSION}/candidates`,
    DETAIL: (id: string) => `${API_VERSION}/candidates/${id}`,
    ADD_POSITION: (candidateId: string, positionId: string) =>
      `${API_VERSION}/candidates/${candidateId}/positions/${positionId}`,
  },
  POSITIONS: {
    LIST: `${API_VERSION}/positions`,
    DETAIL: (id: string) => `${API_VERSION}/positions/${id}`,
    UPDATE: (id: string) => `${API_VERSION}/positions/${id}`,
  },
};
