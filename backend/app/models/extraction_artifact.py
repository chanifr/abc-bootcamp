import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ArtifactType(str, enum.Enum):
    HEURISTIC = "heuristic"
    LLM = "llm"


class ArtifactStatus(str, enum.Enum):
    SUCCESS = "success"
    VALIDATION_FAILED = "validation_failed"
    LLM_ERROR = "llm_error"


class ExtractionArtifact(Base):
    """Stores the full I/O of one extraction stage for auditability.

    For heuristic artifacts: artifact_type=heuristic, validated_output=JSON.
    For LLM artifacts: all fields populated.

    raw_llm_output is kept verbatim so failures can be inspected.
    validated_output is only written on success.
    """

    __tablename__ = "extraction_artifacts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    ingestion_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("document_ingestions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    artifact_type: Mapped[ArtifactType] = mapped_column(
        Enum(ArtifactType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    # Prompt identity — null for heuristic artifacts
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Raw I/O — null for heuristic artifacts
    raw_llm_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_llm_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Structured results
    validated_output: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    status: Mapped[ArtifactStatus] = mapped_column(
        Enum(ArtifactStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ArtifactStatus.SUCCESS,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Cost / observability metadata
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    ingestion: Mapped["DocumentIngestion"] = relationship(
        "DocumentIngestion", back_populates="artifacts"
    )

    def __repr__(self) -> str:
        return f"<ExtractionArtifact {self.artifact_type} [{self.status}]>"
