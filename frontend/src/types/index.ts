export type CandidateStatus = 'Active' | 'Inactive' | 'Hired';
export type PositionStatus = 'Open' | 'Closed' | 'On Hold';
export type DocumentType = 'CV' | 'Resume' | 'Cover Letter';
export type SkillLevel = 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert';

export interface Experience {
  id: string;
  company: string;
  title: string;
  startDate: string;
  endDate: string | null;
  description: string;
  sortOrder: number;
}

export interface Education {
  id: string;
  institution: string;
  degree: string;
  field: string;
  graduationDate: string | null;
  sortOrder: number;
}

export interface Skill {
  id: string;
  name: string;
  level: SkillLevel;
  sortOrder: number;
}

export interface Document {
  id: string;
  filename: string;
  type: DocumentType;
  path: string;
  uploadDate: string;
}

export interface Candidate {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  status: CandidateStatus;
  appliedPositions: string[];
  experience: Experience[];
  education: Education[];
  skills: Skill[];
  originalDocuments: Document[];
  notes: string;
  createdAt: string;
  updatedAt: string;
}

export interface PositionRequirements {
  experience: string;
  education: string;
  skills: string[];
}

export interface Position {
  id: string;
  title: string;
  department: string;
  status: PositionStatus;
  description: string;
  requirements: PositionRequirements;
  candidates: string[];
  createdAt: string;
  updatedAt: string;
}
