import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ensureAuthenticated } from '../utils/autoLogin';
import {
  triggerIngestion,
  listIngestionRuns,
  getIngestionRun,
} from '../api/ingestion';
import type { IngestionRun, ArtifactOut } from '../api/ingestion';

// ─── helpers ────────────────────────────────────────────────────────────────

function statusBadge(status: string) {
  const colours: Record<string, string> = {
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    processing: 'bg-yellow-100 text-yellow-800',
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colours[status] ?? 'bg-gray-100 text-gray-800'}`}>
      {status}
    </span>
  );
}

function fileName(path: string) {
  return path.split('/').pop() ?? path;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString();
}

// ─── Artifact detail ─────────────────────────────────────────────────────────

function ArtifactCard({ artifact }: { artifact: ArtifactOut }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-gray-200 rounded-md overflow-hidden">
      <button
        onClick={() => setExpanded(e => !e)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 text-left"
      >
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono uppercase text-gray-500 w-20">{artifact.artifact_type}</span>
          {statusBadge(artifact.status)}
          {artifact.prompt_version && (
            <span className="text-xs text-gray-400 font-mono">{artifact.prompt_version}</span>
          )}
          {artifact.provider && (
            <span className="text-xs text-gray-400">{artifact.provider} / {artifact.model_name}</span>
          )}
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-400">
          {artifact.input_tokens != null && (
            <span>{artifact.input_tokens}↑ {artifact.output_tokens}↓ tokens</span>
          )}
          {artifact.latency_ms != null && <span>{artifact.latency_ms} ms</span>}
          <span>{expanded ? '▲' : '▼'}</span>
        </div>
      </button>

      {expanded && (
        <div className="px-4 py-3 space-y-3 text-sm">
          {artifact.error_message && (
            <div className="bg-red-50 border border-red-200 rounded p-3 text-red-700 text-xs font-mono whitespace-pre-wrap">
              {artifact.error_message}
            </div>
          )}
          {artifact.validated_output && (
            <pre className="bg-gray-50 border border-gray-200 rounded p-3 text-xs overflow-auto max-h-64">
              {JSON.stringify(artifact.validated_output, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Run detail panel ─────────────────────────────────────────────────────────

function RunDetail({ run }: { run: IngestionRun }) {
  return (
    <div className="mt-4 space-y-3">
      <div className="text-xs text-gray-500 font-mono break-all">{run.source_path}</div>

      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
        <span>Type: <strong>{run.document_type}</strong></span>
        {run.candidate_id && (
          <span>
            Candidate:{' '}
            <Link to={`/candidates/${run.candidate_id}`} className="text-blue-600 hover:underline font-mono text-xs">
              {run.candidate_id.slice(0, 8)}…
            </Link>
          </span>
        )}
        {run.position_id && (
          <span>
            Position:{' '}
            <Link to={`/positions/${run.position_id}`} className="text-blue-600 hover:underline font-mono text-xs">
              {run.position_id.slice(0, 8)}…
            </Link>
          </span>
        )}
      </div>

      {run.error_message && (
        <div className="bg-red-50 border border-red-200 rounded p-3 text-red-700 text-xs font-mono whitespace-pre-wrap">
          {run.error_message}
        </div>
      )}

      <div className="space-y-2">
        {run.artifacts.map(a => <ArtifactCard key={a.id} artifact={a} />)}
      </div>
    </div>
  );
}

// ─── Run row ─────────────────────────────────────────────────────────────────

function RunRow({ run }: { run: IngestionRun }) {
  const [expanded, setExpanded] = useState(false);
  const [detail, setDetail] = useState<IngestionRun | null>(null);
  const [loading, setLoading] = useState(false);

  const toggle = async () => {
    if (!expanded && !detail) {
      setLoading(true);
      try {
        const d = await getIngestionRun(run.id);
        setDetail(d);
      } finally {
        setLoading(false);
      }
    }
    setExpanded(e => !e);
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={toggle}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 text-left"
      >
        <div className="flex items-center gap-3 min-w-0">
          {statusBadge(run.status)}
          <span className="text-sm font-medium text-gray-900 truncate">{fileName(run.source_path)}</span>
          <span className="text-xs text-gray-400 hidden sm:inline">{run.document_type}</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-400 ml-2 flex-shrink-0">
          <span>{formatDate(run.created_at)}</span>
          <span>{expanded ? '▲' : '▼'}</span>
        </div>
      </button>

      {expanded && (
        <div className="px-4 pb-4 border-t border-gray-100">
          {loading ? (
            <p className="text-sm text-gray-500 mt-3">Loading...</p>
          ) : detail ? (
            <RunDetail run={detail} />
          ) : null}
        </div>
      )}
    </div>
  );
}

// ─── Main page ───────────────────────────────────────────────────────────────

export const IngestionPage = () => {
  const [sourcePath, setSourcePath] = useState('');
  const [docType, setDocType] = useState('cv');
  const [submitting, setSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<{ ok: boolean; message: string } | null>(null);

  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [runsLoading, setRunsLoading] = useState(true);

  const loadRuns = async () => {
    setRunsLoading(true);
    try {
      const data = await listIngestionRuns();
      setRuns(data);
    } finally {
      setRunsLoading(false);
    }
  };

  useEffect(() => {
    ensureAuthenticated().then(loadRuns);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sourcePath.trim()) return;

    setSubmitting(true);
    setSubmitResult(null);
    try {
      const res = await triggerIngestion({ source_path: sourcePath.trim(), document_type: docType });
      if (res.status === 'completed') {
        setSubmitResult({ ok: true, message: `Ingested successfully. ${res.candidate_id ? `Candidate: ${res.candidate_id}` : `Position: ${res.position_id}`}` });
      } else {
        setSubmitResult({ ok: false, message: res.error ?? 'Ingestion failed' });
      }
      await loadRuns();
      setSourcePath('');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Request failed';
      setSubmitResult({ ok: false, message });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Document Ingestion</h1>
        <p className="mt-2 text-sm text-gray-600">
          Ingest CV or job description files via the server-side pipeline
        </p>
      </div>

      {/* Ingest form */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Ingest a document</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="source-path" className="block text-sm font-medium text-gray-700 mb-1">
              Server-side file path
            </label>
            <input
              id="source-path"
              type="text"
              value={sourcePath}
              onChange={e => setSourcePath(e.target.value)}
              placeholder="/home/develeap/ABC/data_hellio_hr/cvs/cv_003.pdf"
              className="block w-full rounded-md border border-gray-300 px-4 py-2 text-sm font-mono focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <p className="mt-1 text-xs text-gray-400">
              CVs: <span className="font-mono">/home/develeap/ABC/data_hellio_hr/cvs/cv_*.pdf</span> &nbsp;|&nbsp;
              Jobs: <span className="font-mono">/home/develeap/ABC/data_hellio_hr/jobs/job_*.txt</span>
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div>
              <label htmlFor="doc-type" className="block text-sm font-medium text-gray-700 mb-1">
                Document type
              </label>
              <select
                id="doc-type"
                value={docType}
                onChange={e => setDocType(e.target.value)}
                className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="cv">CV / Resume</option>
                <option value="job_description">Job Description</option>
              </select>
            </div>

            <div className="pt-6">
              <button
                type="submit"
                disabled={submitting || !sourcePath.trim()}
                className="inline-flex items-center px-5 py-2 rounded-md bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? 'Ingesting…' : 'Ingest'}
              </button>
            </div>
          </div>

          {submitResult && (
            <div className={`rounded-md px-4 py-3 text-sm ${submitResult.ok ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
              {submitResult.message}
            </div>
          )}
        </form>
      </div>

      {/* Run history */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent runs</h2>
          <button
            onClick={loadRuns}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Refresh
          </button>
        </div>

        {runsLoading ? (
          <p className="text-sm text-gray-500">Loading runs…</p>
        ) : runs.length === 0 ? (
          <p className="text-sm text-gray-500">No ingestion runs yet.</p>
        ) : (
          <div className="space-y-2">
            {runs.map(run => <RunRow key={run.id} run={run} />)}
          </div>
        )}
      </div>
    </div>
  );
};
