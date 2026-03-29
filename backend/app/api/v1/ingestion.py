"""Ingestion API — trigger document ingestion via HTTP.

POST /api/v1/ingestion/ingest
  Body: { "source_path": "...", "document_type": "cv|job_description",
          "provider": "bedrock|anthropic" (optional),
          "model": "..." (optional) }
  Requires editor or admin role.

GET /api/v1/ingestion/runs
  List recent ingestion runs with status and linked entity IDs.

GET /api/v1/ingestion/runs/{id}
  Full detail for one ingestion run including all artifacts.
"""
import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_editor
from app.config import settings
from app.db.session import get_db
from app.models.document_ingestion import DocumentIngestion, IngestionDocType
from app.models.extraction_artifact import ExtractionArtifact
from app.services.ingestion.pipeline import run_ingestion
from app.services.ingestion.providers import build_provider

router = APIRouter()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class IngestRequest(BaseModel):
    source_path: str
    document_type: str  # "cv" or "job_description"
    provider: str | None = None
    model: str | None = None


class ArtifactOut(BaseModel):
    id: str
    artifact_type: str
    prompt_version: str | None
    provider: str | None
    model_name: str | None
    status: str
    error_message: str | None
    input_tokens: int | None
    output_tokens: int | None
    latency_ms: int | None
    validated_output: dict | None

    @classmethod
    def from_orm(cls, a: ExtractionArtifact) -> "ArtifactOut":
        validated = None
        if a.validated_output:
            try:
                validated = json.loads(a.validated_output)
            except Exception:
                validated = None
        return cls(
            id=a.id,
            artifact_type=a.artifact_type.value,
            prompt_version=a.prompt_version,
            provider=a.provider,
            model_name=a.model_name,
            status=a.status.value,
            error_message=a.error_message,
            input_tokens=a.input_tokens,
            output_tokens=a.output_tokens,
            latency_ms=a.latency_ms,
            validated_output=validated,
        )


class IngestionRunOut(BaseModel):
    id: str
    source_path: str
    file_hash: str
    document_type: str
    status: str
    error_message: str | None
    candidate_id: str | None
    position_id: str | None
    created_at: str
    artifacts: list[ArtifactOut] = []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    req: IngestRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_editor),
):
    """Trigger ingestion of a single document by server-side path."""
    path = Path(req.source_path)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File not found on server: {req.source_path}",
        )

    try:
        IngestionDocType(req.document_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document_type {req.document_type!r}. Use 'cv' or 'job_description'.",
        )

    provider_name = req.provider or settings.INGESTION_PROVIDER
    model = req.model or settings.INGESTION_MODEL

    try:
        provider = build_provider(
            provider_name=provider_name,
            model=model,
            region=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_bearer_token=settings.AWS_BEARER_TOKEN_BEDROCK,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    ingestion = await run_ingestion(
        session=db,
        path=path,
        provider=provider,
        document_type=req.document_type,
    )

    return {
        "ingestion_id": ingestion.id,
        "status": ingestion.status.value,
        "candidate_id": ingestion.candidate_id,
        "position_id": ingestion.position_id,
        "error": ingestion.error_message,
    }


@router.get("/runs", response_model=list[IngestionRunOut])
async def list_ingestion_runs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """List the most recent ingestion runs."""
    result = await db.execute(
        select(DocumentIngestion)
        .options(selectinload(DocumentIngestion.artifacts))
        .order_by(DocumentIngestion.created_at.desc())
        .limit(limit)
    )
    runs = result.scalars().all()
    return [_run_to_out(r) for r in runs]


@router.get("/runs/{ingestion_id}", response_model=IngestionRunOut)
async def get_ingestion_run(
    ingestion_id: str,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Full detail for one ingestion run including all artifacts."""
    result = await db.execute(
        select(DocumentIngestion)
        .options(selectinload(DocumentIngestion.artifacts))
        .where(DocumentIngestion.id == ingestion_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return _run_to_out(run)


def _run_to_out(run: DocumentIngestion) -> IngestionRunOut:
    return IngestionRunOut(
        id=run.id,
        source_path=run.source_path,
        file_hash=run.file_hash,
        document_type=run.document_type.value,
        status=run.status.value,
        error_message=run.error_message,
        candidate_id=run.candidate_id,
        position_id=run.position_id,
        created_at=run.created_at.isoformat(),
        artifacts=[ArtifactOut.from_orm(a) for a in (run.artifacts or [])],
    )
