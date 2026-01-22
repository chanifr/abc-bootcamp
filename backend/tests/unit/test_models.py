"""Unit tests for database models."""

import pytest
from datetime import date, datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole
from app.models.candidate import Candidate, CandidateStatus
from app.models.position import Position, PositionStatus
from app.models.experience import Experience
from app.models.education import Education
from app.models.skill import Skill, SkillLevel
from app.models.document import Document, DocumentType
from app.models.position_skill import PositionSkill
from app.models.candidate_position import CandidatePosition


@pytest.mark.asyncio
async def test_create_user(db_session):
    """Test creating a user model."""
    user = User(
        email="test@example.com",
        hashed_password="hashedpw123",
        full_name="Test User",
        role=UserRole.READ_ONLY,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.READ_ONLY
    assert user.is_active is True


@pytest.mark.asyncio
async def test_create_candidate(db_session):
    """Test creating a candidate model."""
    candidate = Candidate(
        name="John Doe",
        email="john@example.com",
        phone="+1234567890",
        location="New York, NY",
        summary="Experienced software engineer",
        status=CandidateStatus.ACTIVE,
    )
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)

    assert candidate.id is not None
    assert candidate.name == "John Doe"
    assert candidate.status == CandidateStatus.ACTIVE
    assert candidate.sort_order == 0


@pytest.mark.asyncio
async def test_create_position(db_session):
    """Test creating a position model."""
    position = Position(
        title="Senior Developer",
        department="Engineering",
        location="Remote",
        description="We are looking for a senior developer",
        requirements="5+ years of experience",
        min_experience_years=5,
        status=PositionStatus.OPEN,
        posted_date=date(2024, 1, 1),
    )
    db_session.add(position)
    await db_session.commit()
    await db_session.refresh(position)

    assert position.id is not None
    assert position.title == "Senior Developer"
    assert position.status == PositionStatus.OPEN


@pytest.mark.asyncio
async def test_candidate_with_experience(db_session):
    """Test creating a candidate with work experience."""
    candidate = Candidate(
        name="Jane Smith",
        email="jane@example.com",
        phone="+1234567890",
        location="Boston, MA",
        summary="Product manager with tech background",
        status=CandidateStatus.ACTIVE,
    )
    db_session.add(candidate)
    await db_session.flush()

    experience = Experience(
        candidate_id=candidate.id,
        company="Tech Corp",
        title="Product Manager",
        start_date=date(2020, 1, 1),
        end_date=None,  # Current job
        description="Leading product development",
    )
    db_session.add(experience)
    await db_session.commit()

    # Verify experience was created and linked
    result = await db_session.execute(
        select(Experience).where(Experience.candidate_id == candidate.id)
    )
    experiences = result.scalars().all()
    assert len(experiences) == 1
    assert experiences[0].company == "Tech Corp"
    assert experiences[0].end_date is None


@pytest.mark.asyncio
async def test_candidate_with_skills(db_session):
    """Test creating a candidate with skills."""
    candidate = Candidate(
        name="Bob Johnson",
        email="bob@example.com",
        phone="+1234567890",
        location="San Francisco, CA",
        summary="Full-stack developer",
        status=CandidateStatus.ACTIVE,
    )
    db_session.add(candidate)
    await db_session.flush()

    skill1 = Skill(candidate_id=candidate.id, name="Python", level=SkillLevel.EXPERT)
    skill2 = Skill(candidate_id=candidate.id, name="React", level=SkillLevel.ADVANCED)
    db_session.add_all([skill1, skill2])
    await db_session.commit()

    # Verify skills were created and linked
    result = await db_session.execute(
        select(Skill).where(Skill.candidate_id == candidate.id)
    )
    skills = result.scalars().all()
    assert len(skills) == 2
    skill_names = {skill.name for skill in skills}
    assert "Python" in skill_names
    assert "React" in skill_names


@pytest.mark.asyncio
async def test_candidate_position_relationship(db_session):
    """Test many-to-many relationship between candidates and positions."""
    candidate = Candidate(
        name="Alice Williams",
        email="alice@example.com",
        phone="+1234567890",
        location="Seattle, WA",
        summary="DevOps engineer",
        status=CandidateStatus.ACTIVE,
    )
    position = Position(
        title="DevOps Engineer",
        department="Infrastructure",
        location="Remote",
        description="Looking for DevOps expertise",
        requirements="3+ years experience",
        min_experience_years=3,
        status=PositionStatus.OPEN,
        posted_date=date(2024, 1, 15),
    )
    db_session.add_all([candidate, position])
    await db_session.flush()

    # Create relationship
    candidate_position = CandidatePosition(
        candidate_id=candidate.id,
        position_id=position.id,
    )
    db_session.add(candidate_position)
    await db_session.commit()

    # Verify junction table records were created
    result = await db_session.execute(
        select(CandidatePosition).where(
            CandidatePosition.candidate_id == candidate.id,
            CandidatePosition.position_id == position.id
        )
    )
    cp_record = result.scalar_one()
    assert cp_record.candidate_id == candidate.id
    assert cp_record.position_id == position.id


@pytest.mark.asyncio
async def test_cascade_delete_candidate(db_session):
    """Test that deleting a candidate cascades to related records."""
    candidate = Candidate(
        name="Tom Brown",
        email="tom@example.com",
        phone="+1234567890",
        location="Austin, TX",
        summary="Data scientist",
        status=CandidateStatus.ACTIVE,
    )
    db_session.add(candidate)
    await db_session.flush()

    # Add related records
    experience = Experience(
        candidate_id=candidate.id,
        company="Data Inc",
        title="Data Scientist",
        start_date=date(2019, 1, 1),
        end_date=date(2023, 12, 31),
        description="ML and analytics",
    )
    skill = Skill(candidate_id=candidate.id, name="Machine Learning", level=SkillLevel.EXPERT)
    db_session.add_all([experience, skill])
    await db_session.commit()

    candidate_id = candidate.id

    # Delete candidate
    await db_session.delete(candidate)
    await db_session.commit()

    # Verify cascades worked - related records should be gone
    from sqlalchemy import select

    exp_result = await db_session.execute(
        select(Experience).where(Experience.candidate_id == candidate_id)
    )
    assert exp_result.scalar_one_or_none() is None

    skill_result = await db_session.execute(
        select(Skill).where(Skill.candidate_id == candidate_id)
    )
    assert skill_result.scalar_one_or_none() is None
