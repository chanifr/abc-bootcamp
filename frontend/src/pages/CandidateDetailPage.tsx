import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getCandidateById, getPositionsByCandidateId, formatDate } from '../utils/dataHelpers';
import { ensureAuthenticated } from '../utils/autoLogin';
import { Card } from '../components/shared/Card';
import type { Candidate, Position } from '../types';

export const CandidateDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [candidate, setCandidate] = useState<Candidate | undefined>();
  const [appliedPositions, setAppliedPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCandidate = async () => {
      if (!id) {
        setLoading(false);
        return;
      }

      await ensureAuthenticated();
      const candidateData = await getCandidateById(id);
      setCandidate(candidateData);

      if (candidateData) {
        const positions = await getPositionsByCandidateId(id);
        setAppliedPositions(positions);
      }

      setLoading(false);
    };
    loadCandidate();
  }, [id]);

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Loading candidate...</p>
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">Candidate not found</h2>
        <Link to="/" className="mt-4 text-blue-600 hover:text-blue-800">
          Back to Candidates
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/" className="text-sm text-blue-600 hover:text-blue-800 mb-2 inline-block">
            ← Back to Candidates
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">
            {candidate.firstName} {candidate.lastName}
          </h1>
        </div>
        <Link
          to={`/candidates/compare?candidates=${candidate.id}`}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Compare Candidate
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Contact Information */}
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Information</h2>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="mt-1 text-sm text-gray-900">{candidate.email}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Phone</dt>
                <dd className="mt-1 text-sm text-gray-900">{candidate.phone}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {candidate.status}
                  </span>
                </dd>
              </div>
            </dl>
          </Card>

          {/* Experience */}
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Experience</h2>
            {candidate.experience.length === 0 ? (
              <p className="text-sm text-gray-500">No experience listed</p>
            ) : (
              <div className="space-y-6">
                {candidate.experience.map(exp => (
                  <div key={exp.id} className="relative pl-8 pb-6 border-l-2 border-gray-200 last:pb-0">
                    <div className="absolute -left-2 top-0 w-4 h-4 rounded-full bg-blue-500" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{exp.title}</h3>
                      <p className="text-sm font-medium text-gray-700">{exp.company}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        {formatDate(exp.startDate)} - {formatDate(exp.endDate)}
                      </p>
                      <p className="text-sm text-gray-700 mt-3">{exp.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Education */}
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Education</h2>
            {candidate.education.length === 0 ? (
              <p className="text-sm text-gray-500">No education listed</p>
            ) : (
              <div className="space-y-4">
                {candidate.education.map(edu => (
                  <div key={edu.id}>
                    <h3 className="text-lg font-medium text-gray-900">{edu.degree}</h3>
                    <p className="text-sm font-medium text-gray-700">{edu.institution}</p>
                    <p className="text-sm text-gray-600">Field: {edu.field}</p>
                    {edu.graduationDate && (
                      <p className="text-sm text-gray-500 mt-1">
                        Graduated: {formatDate(edu.graduationDate)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Original Documents */}
          {candidate.originalDocuments.length > 0 && (
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Documents</h2>
              <div className="space-y-2">
                {candidate.originalDocuments.map(doc => (
                  <div key={doc.id} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                      <p className="text-xs text-gray-500">
                        {doc.type} • Uploaded {new Date(doc.uploadDate).toLocaleDateString()}
                      </p>
                    </div>
                    <a
                      href={doc.path}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      View
                    </a>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          {/* Skills */}
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Skills</h2>
            {candidate.skills.length === 0 ? (
              <p className="text-sm text-gray-500">No skills listed</p>
            ) : (
              <div className="space-y-3">
                {candidate.skills.map(skill => (
                  <div key={skill.id}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-gray-900">{skill.name}</span>
                      <span className="text-gray-600">{skill.level}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: skill.level === 'Expert' ? '100%' :
                                 skill.level === 'Advanced' ? '75%' :
                                 skill.level === 'Intermediate' ? '50%' : '25%'
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Applied Positions */}
          <Card>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Applied Positions</h2>
            {appliedPositions.length === 0 ? (
              <p className="text-sm text-gray-500">No positions applied</p>
            ) : (
              <div className="space-y-2">
                {appliedPositions.map(position => (
                  <Link
                    key={position.id}
                    to={`/positions/${position.id}`}
                    className="block p-3 bg-gray-50 rounded hover:bg-gray-100"
                  >
                    <p className="text-sm font-medium text-gray-900">{position.title}</p>
                    <p className="text-xs text-gray-600">{position.department}</p>
                  </Link>
                ))}
              </div>
            )}
          </Card>

          {/* Notes */}
          {candidate.notes && (
            <Card>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Notes</h2>
              <p className="text-sm text-gray-700">{candidate.notes}</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
