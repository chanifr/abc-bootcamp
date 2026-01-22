/**
 * API Response Types (matching backend schema)
 */

export interface APICandidateListItem {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  summary: string;
  status: string;
  yearsOfExperience: number;
  sortOrder: number;
  skills: APISkill[];
  appliedPositions: string[];
}

export interface APICandidateDetail {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  summary: string;
  status: string;
  yearsOfExperience: number;
  sortOrder: number;
  experience: APIExperience[];
  education: APIEducation[];
  skills: APISkill[];
  documents: APIDocument[];
  appliedPositions: string[];
}

export interface APIExperience {
  company: string;
  title: string;
  startDate: string;
  endDate: string | null;
  description: string;
}

export interface APIEducation {
  institution: string;
  degree: string;
  field: string;
  startDate: string;
  endDate: string | null;
}

export interface APISkill {
  name: string;
  level: string;
}

export interface APIDocument {
  type: string;
  name: string;
  url: string;
}

export interface APICandidatesResponse {
  candidates: APICandidateListItem[];
  total: number;
}

export interface APIPositionListItem {
  id: string;
  title: string;
  department: string;
  location: string;
  description: string;
  requirements: string;
  requiredSkills: string[];
  minExperienceYears: number;
  status: string;
  postedDate: string;
  candidates: string[];
  sortOrder: number;
}

export interface APIPositionDetail {
  id: string;
  title: string;
  department: string;
  location: string;
  description: string;
  requirements: string;
  requiredSkills: string[];
  minExperienceYears: number;
  status: string;
  postedDate: string;
  candidates: string[];
  sortOrder: number;
}

export interface APIPositionsResponse {
  positions: APIPositionListItem[];
  total: number;
}
