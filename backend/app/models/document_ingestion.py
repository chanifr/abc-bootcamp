import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IngestionDocType(str, enum.Enum):
    CV = "cv"
    JOB_DESCRIPTION = "job_description"


class IngestionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentIngestion(Base):
    """Tracks one ingestion attempt for a source file.

    A new row is created on every run — even for the same file — so
    multiple runs can be compared.  file_hash (SHA-256) identifies
    duplicate source content across runs.
    """

    __tablename__ = "document_ingestions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    source_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    document_type: Mapped[IngestionDocType] = mapped_column(
        Enum(IngestionDocType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    status: Mapped[IngestionStatus] = mapped_column(
        Enum(IngestionStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=IngestionStatus.PENDING,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Stored as plain strings (not FK-constrained) so the record survives
    # even if the linked candidate/position is later deleted.
    candidate_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    position_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    raw_texts: Mapped[list["RawDocumentText"]] = relationship(
        "RawDocumentText", back_populates="ingestion", cascade="all, delete-orphan"
    )
    artifacts: Mapped[list["ExtractionArtifact"]] = relationship(
        "ExtractionArtifact", back_populates="ingestion", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DocumentIngestion {self.source_path} [{self.status}]>"
