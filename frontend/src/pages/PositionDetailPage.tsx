import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getPositionById, getCandidatesByPositionId, calculateYearsOfExperience } from '../utils/dataHelpers';
import { ensureAuthenticated } from '../utils/autoLogin';
import { Card } from '../components/shared/Card';
import type { Position, Candidate } from '../types';

export const PositionDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [position, setPosition] = useState<Position | undefined>();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPosition = async () => {
      if (!id) {
        setLoading(false);
        return;
      }

      await ensureAuthenticated();
      const positionData = await getPositionById(id);
      setPosition(positionData);

      if (positionData) {
        const candidatesData = await getCandidatesByPositionId(id);
        setCandidates(candidatesData);
      }

      setLoading(false);
    };
    loadPosition();
  }, [id]);

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Loading position...</p>
      </div>
    );
  }

  if (!position) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">Position not found</h2>
        <Link to="/positions" className="mt-4 text-blue-600 hover:text-blue-800">
          Back to Positions
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <Link to="/positions" className="text-sm text-blue-600 hover:text-blue-800 mb-2 inline-block">
          ← Back to Positions
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-bold text-gray-900">{position.title}</h1>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            {position.status}
          </span>
        </div>
        <p className="mt-2 text-sm text-gray-600">{position.department}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Position Description</h2>
            <div className="prose prose-sm max-w-none">
              {position.description.split('\n').map((paragraph, index) => (
                paragraph.trim() && (
                  <p key={index} className="text-sm text-gray-700 mb-3">
                    {paragraph}
                  </p>
                )
              ))}
            </div>
          </Card>

          {/* Candidates */}
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Candidates ({candidates.length})
            </h2>
            {candidates.length === 0 ? (
              <p className="text-sm text-gray-500">No candidates have applied yet.</p>
            ) : (
              <div className="space-y-4">
                {candidates.map(candidate => {
                  const yearsExp = calculateYearsOfExperience(candidate);
                  const currentRole = candidate.experience.find(e => e.endDate === null);

                  return (
                    <div key={candidate.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h3 className="text-base font-semibold text-gray-900">
                              {candidate.firstName} {candidate.lastName}
                            </h3>
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              {candidate.status}
                            </span>
                          </div>

                          {currentRole && (
                            <p className="text-sm text-gray-600 mt-1">
                              {currentRole.title} at {currentRole.company}
                            </p>
                          )}

                          <p className="text-sm text-gray-500 mt-1">
                            {yearsExp} years of experience
                          </p>

                          <div className="mt-2 flex flex-wrap gap-1">
                            {candidate.skills.slice(0, 4).map(skill => (
                              <span
                                key={skill.id}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700"
                              >
                                {skill.name}
                              </span>
                            ))}
                            {candidate.skills.length > 4 && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs text-gray-500">
                                +{candidate.skills.length - 4}
                              </span>
                            )}
                          </div>
                        </div>

                        <Link
                          to={`/candidates/${candidate.id}`}
                          className="ml-4 text-sm font-medium text-blue-600 hover:text-blue-800"
                        >
                          View Profile
                        </Link>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          {/* Requirements */}
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Requirements</h2>

            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Experience</h3>
                <p className="text-sm text-gray-600">{position.requirements.experience}</p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Education</h3>
                <p className="text-sm text-gray-600">{position.requirements.education}</p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Required Skills ({position.requirements.skills.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {position.requirements.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </Card>

          {/* Metadata */}
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Details</h2>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="text-sm text-gray-900">
                  {new Date(position.createdAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                <dd className="text-sm text-gray-900">
                  {new Date(position.updatedAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </dd>
              </div>
            </dl>
          </Card>
        </div>
      </div>
    </div>
  );
};
