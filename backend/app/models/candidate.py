import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CandidateStatus(str, enum.Enum):
    """Candidate status enum."""
    ACTIVE = "Active"
    HIRED = "Hired"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


class Candidate(Base):
    """Candidate model."""

    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[CandidateStatus] = mapped_column(
        Enum(CandidateStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CandidateStatus.ACTIVE
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    experiences: Mapped[list["Experience"]] = relationship(
        "Experience", back_populates="candidate", cascade="all, delete-orphan"
    )
    education: Mapped[list["Education"]] = relationship(
        "Education", back_populates="candidate", cascade="all, delete-orphan"
    )
    skills: Mapped[list["Skill"]] = relationship(
        "Skill", back_populates="candidate", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="candidate", cascade="all, delete-orphan"
    )
    # Many-to-many with Position through candidate_positions
    candidate_positions: Mapped[list["CandidatePosition"]] = relationship(
        "CandidatePosition", back_populates="candidate", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Candidate {self.name} ({self.email})>"
