import { Link } from 'react-router-dom';
import type { Position } from '../../types';
import { getCandidatesByPositionId } from '../../utils/dataHelpers';
import { Card } from '../shared/Card';

interface PositionCardProps {
  position: Position;
}

export const PositionCard = ({ position }: PositionCardProps) => {
  const candidates = getCandidatesByPositionId(position.id);

  return (
    <Card className="hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-gray-900">{position.title}</h3>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {position.status}
            </span>
          </div>

          <p className="text-sm text-gray-600 mt-1">{position.department}</p>

          <p className="text-sm text-gray-700 mt-3 line-clamp-2">
            {position.description.split('\n')[0]}
          </p>

          <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
            <span>{candidates.length} candidate{candidates.length !== 1 ? 's' : ''}</span>
            <span>•</span>
            <span>{position.requirements.skills.length} required skills</span>
          </div>
        </div>

        <Link
          to={`/positions/${position.id}`}
          className="ml-4 text-sm font-medium text-blue-600 hover:text-blue-800"
        >
          View Details
        </Link>
      </div>
    </Card>
  );
};
