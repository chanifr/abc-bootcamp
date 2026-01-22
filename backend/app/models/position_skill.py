from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PositionSkill(Base):
    """Required skills for a position."""

    __tablename__ = "position_skills"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    position_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("positions.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    position: Mapped["Position"] = relationship("Position", back_populates="required_skills")

    def __repr__(self) -> str:
        return f"<PositionSkill {self.name}>"
