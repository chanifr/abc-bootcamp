/**
 * Data mappers to convert API responses to frontend types
 */

import type {
  APICandidateListItem,
  APICandidateDetail,
  APIPositionListItem,
  APIPositionDetail,
} from '../api/types';
import type { Candidate, Position, Experience, Education, Skill, Document } from '../types';

/**
 * Split full name into first and last name
 */
function splitName(fullName: string): { firstName: string; lastName: string } {
  const parts = fullName.trim().split(' ');
  if (parts.length === 1) {
    return { firstName: parts[0], lastName: '' };
  }
  const firstName = parts[0];
  const lastName = parts.slice(1).join(' ');
  return { firstName, lastName };
}

/**
 * Generate a simple UUID-like ID
 */
function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Map API Experience to frontend Experience
 */
function mapExperience(exp: any, index: number): Experience {
  return {
    id: generateId(),
    company: exp.company,
    title: exp.title,
    startDate: exp.startDate,
    endDate: exp.endDate,
    description: exp.description,
    sortOrder: index,
  };
}

/**
 * Map API Education to frontend Education
 */
function mapEducation(edu: any, index: number): Education {
  return {
    id: generateId(),
    institution: edu.institution,
    degree: edu.degree,
    field: edu.field,
    graduationDate: edu.endDate,
    sortOrder: index,
  };
}

/**
 * Map API Skill to frontend Skill
 */
function mapSkill(skill: any, index: number): Skill {
  return {
    id: generateId(),
    name: skill.name,
    level: skill.level as any,
    sortOrder: index,
  };
}

/**
 * Map API Document to frontend Document
 */
function mapDocument(doc: any): Document {
  return {
    id: generateId(),
    filename: doc.name,
    type: doc.type as any,
    path: doc.url,
    uploadDate: new Date().toISOString(),
  };
}

/**
 * Map API Candidate List Item to frontend Candidate (minimal data)
 */
export function mapCandidateListItem(apiCandidate: APICandidateListItem): Candidate {
  const { firstName, lastName } = splitName(apiCandidate.name);

  return {
    id: apiCandidate.id,
    firstName,
    lastName,
    email: apiCandidate.email,
    phone: apiCandidate.phone,
    status: apiCandidate.status as any,
    appliedPositions: apiCandidate.appliedPositions,
    experience: [],
    education: [],
    skills: apiCandidate.skills.map((s, i) => mapSkill(s, i)),
    originalDocuments: [],
    notes: '',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
}

/**
 * Map API Candidate Detail to frontend Candidate (full data)
 */
export function mapCandidateDetail(apiCandidate: APICandidateDetail): Candidate {
  const { firstName, lastName } = splitName(apiCandidate.name);

  return {
    id: apiCandidate.id,
    firstName,
    lastName,
    email: apiCandidate.email,
    phone: apiCandidate.phone,
    status: apiCandidate.status as any,
    appliedPositions: apiCandidate.appliedPositions,
    experience: apiCandidate.experience.map((e, i) => mapExperience(e, i)),
    education: apiCandidate.education.map((e, i) => mapEducation(e, i)),
    skills: apiCandidate.skills.map((s, i) => mapSkill(s, i)),
    originalDocuments: apiCandidate.documents.map(mapDocument),
    notes: '',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
}

/**
 * Map API Position to frontend Position
 */
export function mapPosition(apiPosition: APIPositionListItem | APIPositionDetail): Position {
  return {
    id: apiPosition.id,
    title: apiPosition.title,
    department: apiPosition.department,
    status: apiPosition.status as any,
    description: apiPosition.description,
    requirements: {
      experience: `${apiPosition.minExperienceYears}+ years`,
      education: '',
      skills: apiPosition.requiredSkills,
    },
    candidates: apiPosition.candidates,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
}
