import { Link } from 'react-router-dom';
import type { Candidate } from '../../types';
import { calculateYearsOfExperience, getPositionsByCandidateId } from '../../utils/dataHelpers';
import { Card } from '../shared/Card';

interface CandidateCardProps {
  candidate: Candidate;
}

export const CandidateCard = ({ candidate }: CandidateCardProps) => {
  const positions = getPositionsByCandidateId(candidate.id);
  const yearsExp = calculateYearsOfExperience(candidate);
  const currentRole = candidate.experience.find(e => e.endDate === null);

  return (
    <Card className="hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-gray-900">
              {candidate.firstName} {candidate.lastName}
            </h3>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              {candidate.status}
            </span>
          </div>

          {currentRole && (
            <p className="text-sm text-gray-600 mt-1">
              {currentRole.title} at {currentRole.company}
            </p>
          )}

          <div className="mt-3 flex flex-wrap gap-2">
            {candidate.skills.slice(0, 5).map(skill => (
              <span
                key={skill.id}
                className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-50 text-blue-700"
              >
                {skill.name}
              </span>
            ))}
            {candidate.skills.length > 5 && (
              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium text-gray-500">
                +{candidate.skills.length - 5} more
              </span>
            )}
          </div>

          <div className="mt-3 text-sm text-gray-500">
            <p>{yearsExp} years of experience</p>
            {positions.length > 0 && (
              <p className="mt-1">
                Applied to: {positions.map(p => p.title).join(', ')}
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-2 ml-4">
          <Link
            to={`/candidates/${candidate.id}`}
            className="text-sm font-medium text-blue-600 hover:text-blue-800"
          >
            View Details
          </Link>
          <Link
            to={`/candidates/compare?candidates=${candidate.id}`}
            className="text-sm font-medium text-gray-600 hover:text-gray-800"
          >
            Compare
          </Link>
        </div>
      </div>
    </Card>
  );
};
