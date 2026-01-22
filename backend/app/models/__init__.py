# Import all models for Alembic to detect
from app.models.candidate import Candidate, CandidateStatus
from app.models.candidate_position import CandidatePosition
from app.models.document import Document, DocumentType
from app.models.education import Education
from app.models.experience import Experience
from app.models.position import Position, PositionStatus
from app.models.position_skill import PositionSkill
from app.models.skill import Skill, SkillLevel
from app.models.user import User, UserRole

__all__ = [
    "User",
    "UserRole",
    "Candidate",
    "CandidateStatus",
    "Position",
    "PositionStatus",
    "Experience",
    "Education",
    "Skill",
    "SkillLevel",
    "Document",
    "DocumentType",
    "PositionSkill",
    "CandidatePosition",
]
