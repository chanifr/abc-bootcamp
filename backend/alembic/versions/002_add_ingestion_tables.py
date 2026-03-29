"""add ingestion tables

Revision ID: 002
Revises: 001
Create Date: 2026-03-23 00:00:00.000000

Adds three tables for Exercise 3 (unstructured document ingestion):
  document_ingestions  — one row per ingestion attempt (audit + idempotency)
  raw_document_texts   — raw extracted text, separate from structured output
  extraction_artifacts — full I/O of each extraction stage (heuristic + LLM)
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "document_ingestions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_path", sa.String(512), nullable=False),
        sa.Column("file_hash", sa.String(64), nullable=False),
        sa.Column(
            "document_type",
            sa.Enum("cv", "job_description", name="ingestiondoctype"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "completed", "failed", name="ingestionstatus"),
            nullable=False,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        # Stored without FK constraint intentionally — record should survive
        # even if the linked candidate/position is later deleted.
        sa.Column("candidate_id", sa.String(36), nullable=True),
        sa.Column("position_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_document_ingestions_file_hash", "document_ingestions", ["file_hash"])

    op.create_table(
        "raw_document_texts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ingestion_id", sa.String(36), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("parser_used", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ingestion_id"], ["document_ingestions.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_raw_document_texts_ingestion_id", "raw_document_texts", ["ingestion_id"]
    )

    op.create_table(
        "extraction_artifacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ingestion_id", sa.String(36), nullable=False),
        sa.Column(
            "artifact_type",
            sa.Enum("heuristic", "llm", name="artifacttype"),
            nullable=False,
        ),
        sa.Column("prompt_version", sa.String(50), nullable=True),
        sa.Column("provider", sa.String(50), nullable=True),
        sa.Column("model_name", sa.String(100), nullable=True),
        sa.Column("raw_llm_input", sa.Text(), nullable=True),
        sa.Column("raw_llm_output", sa.Text(), nullable=True),
        sa.Column("validated_output", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("success", "validation_failed", "llm_error", name="artifactstatus"),
            nullable=False,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ingestion_id"], ["document_ingestions.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_extraction_artifacts_ingestion_id", "extraction_artifacts", ["ingestion_id"]
    )


def downgrade() -> None:
    op.drop_table("extraction_artifacts")
    op.drop_table("raw_document_texts")
    op.drop_table("document_ingestions")
    op.execute("DROP TYPE IF EXISTS artifactstatus")
    op.execute("DROP TYPE IF EXISTS artifacttype")
    op.execute("DROP TYPE IF EXISTS ingestionstatus")
    op.execute("DROP TYPE IF EXISTS ingestiondoctype")
