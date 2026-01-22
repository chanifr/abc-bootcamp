/**
 * Positions API Service
 */

import { apiRequest } from './client';
import { API_ENDPOINTS } from './config';
import type { APIPositionsResponse, APIPositionDetail } from './types';

export interface GetPositionsParams {
  status?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

export interface UpdatePositionData {
  title?: string;
  department?: string;
  location?: string;
  description?: string;
  requirements?: string;
  minExperienceYears?: number;
  status?: string;
  postedDate?: string;
}

/**
 * Get list of positions with optional filters
 */
export async function getPositions(
  params: GetPositionsParams = {}
): Promise<APIPositionsResponse> {
  const searchParams = new URLSearchParams();

  if (params.status) searchParams.append('status', params.status);
  if (params.search) searchParams.append('search', params.search);
  if (params.limit) searchParams.append('limit', params.limit.toString());
  if (params.offset) searchParams.append('offset', params.offset.toString());

  const query = searchParams.toString();
  const endpoint = query ? `${API_ENDPOINTS.POSITIONS.LIST}?${query}` : API_ENDPOINTS.POSITIONS.LIST;

  return apiRequest<APIPositionsResponse>(endpoint);
}

/**
 * Get a single position by ID
 */
export async function getPositionById(id: string): Promise<APIPositionDetail> {
  return apiRequest<APIPositionDetail>(API_ENDPOINTS.POSITIONS.DETAIL(id));
}

/**
 * Update a position
 */
export async function updatePosition(
  id: string,
  data: UpdatePositionData
): Promise<APIPositionDetail> {
  return apiRequest<APIPositionDetail>(API_ENDPOINTS.POSITIONS.UPDATE(id), {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}
