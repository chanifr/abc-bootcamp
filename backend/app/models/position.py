import enum
from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PositionStatus(str, enum.Enum):
    """Position status enum."""
    OPEN = "Open"
    CLOSED = "Closed"
    ON_HOLD = "On Hold"


class Position(Base):
    """Position model."""

    __tablename__ = "positions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)
    min_experience_years: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[PositionStatus] = mapped_column(
        Enum(PositionStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PositionStatus.OPEN
    )
    posted_date: Mapped[date] = mapped_column(Date, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    required_skills: Mapped[list["PositionSkill"]] = relationship(
        "PositionSkill", back_populates="position", cascade="all, delete-orphan"
    )
    # Many-to-many with Candidate through candidate_positions
    candidate_positions: Mapped[list["CandidatePosition"]] = relationship(
        "CandidatePosition", back_populates="position", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Position {self.title} ({self.department})>"
