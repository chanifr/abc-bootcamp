from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CandidatePosition(Base):
    """Junction table for many-to-many relationship between Candidates and Positions."""

    __tablename__ = "candidate_positions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False
    )
    position_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("positions.id", ondelete="CASCADE"), nullable=False
    )
    applied_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="candidate_positions")
    position: Mapped["Position"] = relationship("Position", back_populates="candidate_positions")

    # Ensure unique candidate-position pairs
    __table_args__ = (
        UniqueConstraint("candidate_id", "position_id", name="uq_candidate_position"),
    )

    def __repr__(self) -> str:
        return f"<CandidatePosition {self.candidate_id} -> {self.position_id}>"
