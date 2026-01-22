import type { Candidate, Position } from '../types';
import { getCandidates, getCandidateById as apiGetCandidateById } from '../api/candidates';
import { getPositions, getPositionById as apiGetPositionById } from '../api/positions';
import { mapCandidateListItem, mapCandidateDetail, mapPosition } from './mappers';

// In-memory cache
let candidatesCache: Candidate[] | null = null;
let positionsCache: Position[] | null = null;

/**
 * Fetch and cache all active candidates
 */
export async function fetchCandidates(): Promise<Candidate[]> {
  if (candidatesCache) {
    return candidatesCache;
  }

  const response = await getCandidates({ status: 'Active' });
  candidatesCache = response.candidates.map(mapCandidateListItem);
  return candidatesCache;
}

/**
 * Fetch and cache all open positions
 */
export async function fetchPositions(): Promise<Position[]> {
  if (positionsCache) {
    return positionsCache;
  }

  const response = await getPositions({ status: 'Open' });
  positionsCache = response.positions.map(mapPosition);
  return positionsCache;
}

/**
 * Clear the cache (useful after updates)
 */
export function clearCache(): void {
  candidatesCache = null;
  positionsCache = null;
}

/**
 * Get candidate by ID (fetches from API)
 */
export async function getCandidateById(id: string): Promise<Candidate | undefined> {
  try {
    const apiCandidate = await apiGetCandidateById(id);
    return mapCandidateDetail(apiCandidate);
  } catch (error) {
    console.error('Error fetching candidate:', error);
    return undefined;
  }
}

/**
 * Get position by ID (fetches from API)
 */
export async function getPositionById(id: string): Promise<Position | undefined> {
  try {
    const apiPosition = await apiGetPositionById(id);
    return mapPosition(apiPosition);
  } catch (error) {
    console.error('Error fetching position:', error);
    return undefined;
  }
}

/**
 * Get candidates by position ID
 */
export async function getCandidatesByPositionId(positionId: string): Promise<Candidate[]> {
  const response = await getCandidates({ positionId });
  return response.candidates.map(mapCandidateListItem);
}

/**
 * Get positions by candidate ID
 */
export async function getPositionsByCandidateId(candidateId: string): Promise<Position[]> {
  const candidates = await fetchCandidates();
  const candidate = candidates.find(c => c.id === candidateId);
  if (!candidate) return [];

  const positions = await fetchPositions();
  return positions.filter(p => candidate.appliedPositions.includes(p.id));
}

/**
 * Get active candidates
 */
export async function getActiveCandidates(): Promise<Candidate[]> {
  return fetchCandidates();
}

/**
 * Get open positions
 */
export async function getOpenPositions(): Promise<Position[]> {
  return fetchPositions();
}

/**
 * Format date helper
 */
export const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'Present';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
};

/**
 * Calculate years of experience from candidate experience array
 */
export const calculateYearsOfExperience = (candidate: Candidate): number => {
  if (candidate.experience.length === 0) return 0;

  const sortedExperience = [...candidate.experience].sort((a, b) =>
    new Date(a.startDate).getTime() - new Date(b.startDate).getTime()
  );

  const firstJob = sortedExperience[0];
  const lastJob = sortedExperience[sortedExperience.length - 1];

  const startDate = new Date(firstJob.startDate);
  const endDate = lastJob.endDate ? new Date(lastJob.endDate) : new Date();

  const years = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24 * 365);
  return Math.round(years * 10) / 10;
};

/**
 * Search candidates with filters
 */
export async function searchCandidates(query: string, filterPosition?: string): Promise<Candidate[]> {
  // Use API search if no position filter
  if (!filterPosition && query) {
    const response = await getCandidates({ search: query, status: 'Active' });
    return response.candidates.map(mapCandidateListItem);
  }

  // Otherwise fetch and filter locally
  let results = await getActiveCandidates();

  if (filterPosition) {
    results = results.filter(c => c.appliedPositions.includes(filterPosition));
  }

  if (!query) return results;

  const lowerQuery = query.toLowerCase();
  return results.filter(c => {
    const fullName = `${c.firstName} ${c.lastName}`.toLowerCase();
    const email = c.email.toLowerCase();
    const skills = c.skills.map(s => s.name.toLowerCase()).join(' ');
    const companies = c.experience.map(e => e.company.toLowerCase()).join(' ');

    return fullName.includes(lowerQuery) ||
           email.includes(lowerQuery) ||
           skills.includes(lowerQuery) ||
           companies.includes(lowerQuery);
  });
}

// Legacy synchronous exports for backward compatibility (will need to be updated in components)
export const candidates: Candidate[] = [];
export const positions: Position[] = [];
