import { apiRequest } from './client';

export interface IngestRequest {
  source_path: string;
  document_type: string;
}

export interface ArtifactOut {
  id: string;
  artifact_type: string;
  prompt_version: string | null;
  provider: string | null;
  model_name: string | null;
  status: string;
  error_message: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  latency_ms: number | null;
  validated_output: Record<string, unknown> | null;
}

export interface IngestionRun {
  id: string;
  source_path: string;
  file_hash: string;
  document_type: string;
  status: string;
  error_message: string | null;
  candidate_id: string | null;
  position_id: string | null;
  created_at: string;
  artifacts: ArtifactOut[];
}

export interface IngestResponse {
  ingestion_id: string;
  status: string;
  candidate_id: string | null;
  position_id: string | null;
  error: string | null;
}

export async function triggerIngestion(req: IngestRequest): Promise<IngestResponse> {
  return apiRequest<IngestResponse>('/api/v1/ingestion/ingest', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export async function listIngestionRuns(): Promise<IngestionRun[]> {
  return apiRequest<IngestionRun[]>('/api/v1/ingestion/runs');
}

export async function getIngestionRun(id: string): Promise<IngestionRun> {
  return apiRequest<IngestionRun>(`/api/v1/ingestion/runs/${id}`);
}
