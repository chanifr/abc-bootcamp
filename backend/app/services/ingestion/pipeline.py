"""Ingestion pipeline — orchestrates all stages for one document.

Stages (in order):
  1. Load raw text from file
  2. Persist RawDocumentText
  3. Run heuristic extraction; persist heuristic artifact
  4. Run LLM extraction; persist LLM artifact (raw output stored regardless)
  5. Validate LLM output; update artifact with validated_output
  6. Persist candidate or position to main schema tables
  7. Mark DocumentIngestion as completed or failed

Each stage failure is caught and stored — nothing is silently swallowed.
"""
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_ingestion import DocumentIngestion, IngestionDocType, IngestionStatus
from app.models.extraction_artifact import ArtifactStatus, ArtifactType, ExtractionArtifact
from app.models.raw_document_text import RawDocumentText
from app.services.ingestion.document_loader import DocumentLoadError, load_document
from app.services.ingestion.heuristic_extractor import extract_cv_heuristics, extract_job_heuristics
from app.services.ingestion.llm_extractor import LLMExtractionError, extract_async, parse_llm_json
from app.services.ingestion.persistence import PersistenceError, persist_candidate, persist_position
from app.services.ingestion.providers.base import LLMProvider
from app.services.ingestion.validator import ValidationError, validate_cv_extraction, validate_job_extraction

logger = logging.getLogger(__name__)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _detect_document_type(path: Path, explicit: str | None) -> IngestionDocType:
    if explicit:
        return IngestionDocType(explicit)
    # Guess from filename conventions
    name = path.name.lower()
    if name.startswith("cv") or "resume" in name or "curriculum" in name:
        return IngestionDocType.CV
    if "job" in name or name.endswith(".txt"):
        return IngestionDocType.JOB_DESCRIPTION
    raise ValueError(
        f"Cannot infer document type from filename {path.name!r}. "
        "Pass --type cv or --type job explicitly."
    )


async def run_ingestion(
    session: AsyncSession,
    path: Path,
    provider: LLMProvider,
    document_type: str | None = None,
) -> DocumentIngestion:
    """Ingest a single file end-to-end.

    Always creates a new DocumentIngestion row (for comparison across runs).
    On failure, marks the row as failed and stores the error — never raises.
    Returns the DocumentIngestion record regardless of outcome.
    """
    doc_type = _detect_document_type(path, document_type)
    file_hash = _sha256(path)

    ingestion = DocumentIngestion(
        source_path=str(path),
        file_hash=file_hash,
        document_type=doc_type,
        status=IngestionStatus.PROCESSING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(ingestion)
    await session.flush()

    logger.info(
        "Starting ingestion: %s (type=%s, hash=%s)",
        path.name, doc_type.value, file_hash[:12],
    )

    try:
        # Stage 1 — load raw text
        raw_text, parser_used = load_document(path)
        session.add(RawDocumentText(
            ingestion_id=ingestion.id,
            raw_text=raw_text,
            parser_used=parser_used,
            created_at=datetime.utcnow(),
        ))

        # Stage 2 — heuristic extraction
        if doc_type == IngestionDocType.CV:
            heuristic_output = extract_cv_heuristics(raw_text)
        else:
            heuristic_output = extract_job_heuristics(raw_text)

        session.add(ExtractionArtifact(
            ingestion_id=ingestion.id,
            artifact_type=ArtifactType.HEURISTIC,
            validated_output=json.dumps(heuristic_output),
            status=ArtifactStatus.SUCCESS,
            created_at=datetime.utcnow(),
        ))
        logger.info("Heuristic extraction done: %s", heuristic_output)

        # Stage 3 — LLM extraction
        llm_artifact = ExtractionArtifact(
            ingestion_id=ingestion.id,
            artifact_type=ArtifactType.LLM,
            provider=provider.provider_name,
            model_name=provider.model_name,
            status=ArtifactStatus.LLM_ERROR,  # default; updated on success
            created_at=datetime.utcnow(),
        )
        session.add(llm_artifact)

        system_prompt, user_prompt, prompt_version, llm_response = await extract_async(
            raw_text, doc_type.value, provider
        )
        llm_artifact.prompt_version = prompt_version
        llm_artifact.raw_llm_input = user_prompt
        llm_artifact.raw_llm_output = llm_response.content
        llm_artifact.input_tokens = llm_response.input_tokens
        llm_artifact.output_tokens = llm_response.output_tokens
        llm_artifact.latency_ms = llm_response.latency_ms

        logger.info(
            "LLM response received: %s tokens in / %s out, %sms",
            llm_response.input_tokens, llm_response.output_tokens, llm_response.latency_ms,
        )

        # Stage 4 — parse + validate LLM output
        try:
            parsed = parse_llm_json(llm_response.content)
        except ValueError as exc:
            llm_artifact.status = ArtifactStatus.LLM_ERROR
            llm_artifact.error_message = str(exc)
            raise

        try:
            if doc_type == IngestionDocType.CV:
                validated = validate_cv_extraction(parsed)
            else:
                validated = validate_job_extraction(parsed)
        except ValidationError as exc:
            llm_artifact.status = ArtifactStatus.VALIDATION_FAILED
            llm_artifact.error_message = str(exc)
            raise

        llm_artifact.validated_output = json.dumps(validated)
        llm_artifact.status = ArtifactStatus.SUCCESS

        # Stage 5 — persist to main schema
        if doc_type == IngestionDocType.CV:
            record, action = await persist_candidate(
                session, str(path), heuristic_output, validated
            )
            ingestion.candidate_id = record.id
        else:
            record, action = await persist_position(session, heuristic_output, validated)
            ingestion.position_id = record.id

        ingestion.status = IngestionStatus.COMPLETED
        await session.commit()

        logger.info(
            "Ingestion completed: %s %s (id=%s)",
            action, path.name, record.id,
        )

    except (DocumentLoadError, LLMExtractionError, ValidationError, PersistenceError, ValueError) as exc:
        ingestion.status = IngestionStatus.FAILED
        ingestion.error_message = f"{type(exc).__name__}: {exc}"
        ingestion.updated_at = datetime.utcnow()
        await session.commit()
        logger.error("Ingestion FAILED for %s: %s", path.name, exc)

    except Exception as exc:
        ingestion.status = IngestionStatus.FAILED
        ingestion.error_message = f"Unexpected error: {type(exc).__name__}: {exc}"
        ingestion.updated_at = datetime.utcnow()
        await session.commit()
        logger.exception("Unexpected error ingesting %s", path.name)

    return ingestion
