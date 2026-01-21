import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { getCandidateById, getActiveCandidates, formatDate, calculateYearsOfExperience, getPositionsByCandidateId } from '../utils/dataHelpers';
import type { Candidate } from '../types';
import { Card } from '../components/shared/Card';

interface CandidateColumnProps {
  candidate: Candidate | null;
  onSelect: (candidateId: string) => void;
}

const CandidateColumn = ({ candidate, onSelect }: CandidateColumnProps) => {
  const candidates = getActiveCandidates();
  const appliedPositions = candidate ? getPositionsByCandidateId(candidate.id) : [];
  const yearsExp = candidate ? calculateYearsOfExperience(candidate) : 0;

  if (!candidate) {
    return (
      <div className="flex-1">
        <Card>
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Select a Candidate</h3>
            <select
              onChange={(e) => e.target.value && onSelect(e.target.value)}
              className="block w-full max-w-xs mx-auto rounded-md border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              defaultValue=""
            >
              <option value="">Choose a candidate...</option>
              {candidates.map(c => (
                <option key={c.id} value={c.id}>
                  {c.firstName} {c.lastName}
                </option>
              ))}
            </select>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex-1">
      <Card>
        {/* Header */}
        <div className="border-b border-gray-200 pb-4 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {candidate.firstName} {candidate.lastName}
              </h2>
              <p className="text-sm text-gray-600 mt-1">{candidate.email}</p>
            </div>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              {candidate.status}
            </span>
          </div>
          <div className="mt-2">
            <select
              value={candidate.id}
              onChange={(e) => onSelect(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {candidates.map(c => (
                <option key={c.id} value={c.id}>
                  {c.firstName} {c.lastName}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Summary */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Summary</h3>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm font-medium text-gray-700">Experience</dt>
              <dd className="text-sm text-gray-900">{yearsExp} years</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-700">Phone</dt>
              <dd className="text-sm text-gray-900">{candidate.phone}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-700">Applied Positions</dt>
              <dd className="text-sm text-gray-900">
                {appliedPositions.length > 0
                  ? appliedPositions.map(p => p.title).join(', ')
                  : 'None'}
              </dd>
            </div>
          </dl>
        </div>

        {/* Skills */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Skills</h3>
          {candidate.skills.length === 0 ? (
            <p className="text-sm text-gray-500">No skills listed</p>
          ) : (
            <div className="space-y-2">
              {candidate.skills.map(skill => (
                <div key={skill.id} className="flex justify-between items-center">
                  <span className="text-sm text-gray-900">{skill.name}</span>
                  <span className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800">
                    {skill.level}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Experience */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Experience</h3>
          {candidate.experience.length === 0 ? (
            <p className="text-sm text-gray-500">No experience listed</p>
          ) : (
            <div className="space-y-4">
              {candidate.experience.map(exp => (
                <div key={exp.id} className="border-l-2 border-blue-500 pl-3">
                  <h4 className="text-sm font-medium text-gray-900">{exp.title}</h4>
                  <p className="text-sm text-gray-700">{exp.company}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatDate(exp.startDate)} - {formatDate(exp.endDate)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Education */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Education</h3>
          {candidate.education.length === 0 ? (
            <p className="text-sm text-gray-500">No education listed</p>
          ) : (
            <div className="space-y-3">
              {candidate.education.map(edu => (
                <div key={edu.id}>
                  <h4 className="text-sm font-medium text-gray-900">{edu.degree}</h4>
                  <p className="text-sm text-gray-700">{edu.institution}</p>
                  <p className="text-xs text-gray-600">{edu.field}</p>
                  {edu.graduationDate && (
                    <p className="text-xs text-gray-500">{formatDate(edu.graduationDate)}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Documents */}
        {candidate.originalDocuments.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Documents</h3>
            <div className="space-y-2">
              {candidate.originalDocuments.map(doc => (
                <a
                  key={doc.id}
                  href={doc.path}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-sm text-blue-600 hover:text-blue-800"
                >
                  {doc.filename}
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Notes */}
        {candidate.notes && (
          <div>
            <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Notes</h3>
            <p className="text-sm text-gray-700">{candidate.notes}</p>
          </div>
        )}
      </Card>
    </div>
  );
};

export const CandidateComparePage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [candidate1, setCandidate1] = useState<Candidate | null>(null);
  const [candidate2, setCandidate2] = useState<Candidate | null>(null);

  useEffect(() => {
    const candidateIds = searchParams.get('candidates')?.split(',') || [];
    if (candidateIds[0]) {
      const c1 = getCandidateById(candidateIds[0]);
      if (c1) setCandidate1(c1);
    }
    if (candidateIds[1]) {
      const c2 = getCandidateById(candidateIds[1]);
      if (c2) setCandidate2(c2);
    }
  }, [searchParams]);

  const handleSelectCandidate1 = (candidateId: string) => {
    const candidate = getCandidateById(candidateId);
    if (candidate) {
      setCandidate1(candidate);
      const ids = [candidateId, candidate2?.id].filter(Boolean);
      setSearchParams({ candidates: ids.join(',') });
    }
  };

  const handleSelectCandidate2 = (candidateId: string) => {
    const candidate = getCandidateById(candidateId);
    if (candidate) {
      setCandidate2(candidate);
      const ids = [candidate1?.id, candidateId].filter(Boolean);
      setSearchParams({ candidates: ids.join(',') });
    }
  };

  return (
    <div>
      <div className="mb-6">
        <Link to="/" className="text-sm text-blue-600 hover:text-blue-800 mb-2 inline-block">
          ← Back to Candidates
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Compare Candidates</h1>
        <p className="mt-2 text-sm text-gray-600">
          Select two candidates to compare their profiles side by side
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        <CandidateColumn candidate={candidate1} onSelect={handleSelectCandidate1} />
        <CandidateColumn candidate={candidate2} onSelect={handleSelectCandidate2} />
      </div>
    </div>
  );
};
