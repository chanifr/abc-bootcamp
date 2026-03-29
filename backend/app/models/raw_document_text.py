from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RawDocumentText(Base):
    """Raw text extracted from a source file, kept separate from structured output."""

    __tablename__ = "raw_document_texts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    ingestion_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("document_ingestions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parser_used: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    ingestion: Mapped["DocumentIngestion"] = relationship(
        "DocumentIngestion", back_populates="raw_texts"
    )

    def __repr__(self) -> str:
        return f"<RawDocumentText ingestion={self.ingestion_id} parser={self.parser_used}>"
