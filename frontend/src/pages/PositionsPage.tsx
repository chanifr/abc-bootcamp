import { useState } from 'react';
import { PositionCard } from '../components/positions/PositionCard';
import { getOpenPositions } from '../utils/dataHelpers';

export const PositionsPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const openPositions = getOpenPositions();

  const filteredPositions = searchQuery
    ? openPositions.filter(p =>
        p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.requirements.skills.some(s => s.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : openPositions;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Open Positions</h1>
        <p className="mt-2 text-sm text-gray-600">
          Browse and manage open positions
        </p>
      </div>

      <div className="mb-6">
        <label htmlFor="search" className="sr-only">
          Search positions
        </label>
        <input
          type="text"
          id="search"
          placeholder="Search by title, department, or skills..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="block w-full rounded-md border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {filteredPositions.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No positions found matching your criteria.</p>
        </div>
      ) : (
        <>
          <div className="mb-4 text-sm text-gray-600">
            Showing {filteredPositions.length} position{filteredPositions.length !== 1 ? 's' : ''}
          </div>

          <div className="space-y-4">
            {filteredPositions.map(position => (
              <PositionCard key={position.id} position={position} />
            ))}
          </div>
        </>
      )}
    </div>
  );
};
