/**
 * Candidates API Service
 */

import { apiRequest } from './client';
import { API_ENDPOINTS } from './config';
import type { APICandidatesResponse, APICandidateDetail } from './types';

export interface GetCandidatesParams {
  status?: string;
  search?: string;
  positionId?: string;
  limit?: number;
  offset?: number;
}

/**
 * Get list of candidates with optional filters
 */
export async function getCandidates(
  params: GetCandidatesParams = {}
): Promise<APICandidatesResponse> {
  const searchParams = new URLSearchParams();

  if (params.status) searchParams.append('status', params.status);
  if (params.search) searchParams.append('search', params.search);
  if (params.positionId) searchParams.append('positionId', params.positionId);
  if (params.limit) searchParams.append('limit', params.limit.toString());
  if (params.offset) searchParams.append('offset', params.offset.toString());

  const query = searchParams.toString();
  const endpoint = query ? `${API_ENDPOINTS.CANDIDATES.LIST}?${query}` : API_ENDPOINTS.CANDIDATES.LIST;

  return apiRequest<APICandidatesResponse>(endpoint);
}

/**
 * Get a single candidate by ID
 */
export async function getCandidateById(id: string): Promise<APICandidateDetail> {
  return apiRequest<APICandidateDetail>(API_ENDPOINTS.CANDIDATES.DETAIL(id));
}

/**
 * Add a position to a candidate
 */
export async function addPositionToCandidate(
  candidateId: string,
  positionId: string
): Promise<{ message: string }> {
  return apiRequest(API_ENDPOINTS.CANDIDATES.ADD_POSITION(candidateId, positionId), {
    method: 'POST',
  });
}

/**
 * Remove a position from a candidate
 */
export async function removePositionFromCandidate(
  candidateId: string,
  positionId: string
): Promise<{ message: string }> {
  return apiRequest(API_ENDPOINTS.CANDIDATES.ADD_POSITION(candidateId, positionId), {
    method: 'DELETE',
  });
}
