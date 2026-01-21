import type { Candidate, Position } from '../types';
import candidatesData from '../data/candidates.json';
import positionsData from '../data/positions.json';

export const candidates: Candidate[] = candidatesData as Candidate[];
export const positions: Position[] = positionsData as Position[];

export const getCandidateById = (id: string): Candidate | undefined => {
  return candidates.find(c => c.id === id);
};

export const getPositionById = (id: string): Position | undefined => {
  return positions.find(p => p.id === id);
};

export const getCandidatesByPositionId = (positionId: string): Candidate[] => {
  return candidates.filter(c => c.appliedPositions.includes(positionId));
};

export const getPositionsByCandidateId = (candidateId: string): Position[] => {
  const candidate = getCandidateById(candidateId);
  if (!candidate) return [];
  return positions.filter(p => candidate.appliedPositions.includes(p.id));
};

export const getActiveCandidates = (): Candidate[] => {
  return candidates.filter(c => c.status === 'Active');
};

export const getOpenPositions = (): Position[] => {
  return positions.filter(p => p.status === 'Open');
};

export const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'Present';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
};

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

export const searchCandidates = (query: string, filterPosition?: string): Candidate[] => {
  let results = getActiveCandidates();

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
};
