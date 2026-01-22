"""Test data factories using Faker."""

from datetime import date, datetime
from uuid import uuid4

from faker import Faker

from app.models.candidate import Candidate, CandidateStatus
from app.models.document import Document, DocumentType
from app.models.education import Education
from app.models.experience import Experience
from app.models.position import Position, PositionStatus
from app.models.position_skill import PositionSkill
from app.models.skill import Skill, SkillLevel
from app.models.user import User, UserRole

fake = Faker()


def create_user(**kwargs):
    """Create a test user."""
    defaults = {
        "email": fake.email(),
        "hashed_password": "hashed_password",
        "full_name": fake.name(),
        "role": UserRole.READ_ONLY,
        "is_active": True,
    }
    defaults.update(kwargs)
    return User(**defaults)


def create_candidate(**kwargs):
    """Create a test candidate."""
    defaults = {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "location": f"{fake.city()}, {fake.state_abbr()}",
        "summary": fake.text(max_nb_chars=200),
        "status": CandidateStatus.ACTIVE,
        "sort_order": 0,
    }
    defaults.update(kwargs)
    return Candidate(**defaults)


def create_experience(candidate_id: str, **kwargs):
    """Create a test experience record."""
    defaults = {
        "candidate_id": candidate_id,
        "company": fake.company(),
        "title": fake.job(),
        "start_date": date(2020, 1, 1),
        "end_date": date(2023, 12, 31),
        "description": fake.text(max_nb_chars=200),
    }
    defaults.update(kwargs)
    return Experience(**defaults)


def create_education(candidate_id: str, **kwargs):
    """Create a test education record."""
    defaults = {
        "candidate_id": candidate_id,
        "institution": fake.company() + " University",
        "degree": "Bachelor of Science",
        "field": fake.job(),
        "start_date": date(2015, 9, 1),
        "end_date": date(2019, 5, 31),
    }
    defaults.update(kwargs)
    return Education(**defaults)


def create_skill(candidate_id: str, **kwargs):
    """Create a test skill record."""
    defaults = {
        "candidate_id": candidate_id,
        "name": fake.word().capitalize(),
        "level": SkillLevel.INTERMEDIATE,
    }
    defaults.update(kwargs)
    return Skill(**defaults)


def create_document(candidate_id: str, **kwargs):
    """Create a test document record."""
    defaults = {
        "candidate_id": candidate_id,
        "type": DocumentType.CV,
        "name": "resume.pdf",
        "url": f"/storage/documents/{uuid4()}.pdf",
        "uploaded_at": datetime.utcnow(),
    }
    defaults.update(kwargs)
    return Document(**defaults)


def create_position(**kwargs):
    """Create a test position."""
    defaults = {
        "title": fake.job(),
        "department": fake.word().capitalize(),
        "location": f"{fake.city()}, {fake.state_abbr()}",
        "description": fake.text(max_nb_chars=300),
        "requirements": fake.text(max_nb_chars=200),
        "min_experience_years": 3,
        "status": PositionStatus.OPEN,
        "posted_date": date(2024, 1, 1),
        "sort_order": 0,
    }
    defaults.update(kwargs)
    return Position(**defaults)


def create_position_skill(position_id: str, **kwargs):
    """Create a test position skill."""
    defaults = {
        "position_id": position_id,
        "name": fake.word().capitalize(),
    }
    defaults.update(kwargs)
    return PositionSkill(**defaults)
