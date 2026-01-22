"""API tests for candidates endpoints."""

import pytest
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.candidate import CandidateStatus
from app.models.candidate_position import CandidatePosition
from app.models.skill import SkillLevel
from app.models.user import User, UserRole
from tests.fixtures.factories import (
    create_candidate,
    create_document,
    create_education,
    create_experience,
    create_position,
    create_skill,
)


@pytest.fixture
async def auth_token(client: AsyncClient, db_session: AsyncSession) -> str:
    """Create a user and return auth token."""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("password123"),
        full_name="Test User",
        role=UserRole.EDITOR,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password123"},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_get_candidates_requires_auth(client: AsyncClient):
    """Test that getting candidates requires authentication."""
    response = await client.get("/api/v1/candidates")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_candidates_empty(client: AsyncClient, auth_token: str):
    """Test getting candidates when none exist."""
    response = await client.get(
        "/api/v1/candidates",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["candidates"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_candidates_returns_active_only(
    client: AsyncClient, db_session: AsyncSession, auth_token: str
):
    """Test that GET /candidates returns only Active candidates by default."""
    # Create candidates with different statuses
    active = create_candidate(name="Active Candidate", status=CandidateStatus.ACTIVE)
    hired = create_candidate(name="Hired Candidate", status=CandidateStatus.HIRED)
    rejected = create_candidate(name="Rejected Candidate", status=CandidateStatus.REJECTED)

    db_session.add_all([active, hired, rejected])
    await db_session.commit()

    response = await client.get(
        "/api/v1/candidates",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["candidates"]) == 1
    assert data["candidates"][0]["name"] == "Active Candidate"
    assert data["candidates"][0]["status"] == "Active"


@pytest.mark.asyncio
async def test_get_candidates_filter_by_status(
    client: AsyncClient, db_session: AsyncSession, auth_token: str
):
    """Test filtering candidates by status."""
    active = create_candidate(name="Active", status=CandidateStatus.ACTIVE)
    hired = create_candidate(name="Hired", status=CandidateStatus.HIRED)

    db_session.add_all([active, hired])
    await db_session.commit()

    # Filter by Hired status
    response = await client.get(
        "/api/v1/candidates?status=Hired",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["candidates"][0]["name"] == "Hired"


@pytest.mark.asyncio
async def test_search_candidates_by_name(
    client: AsyncClient, db_session: AsyncSession, auth_token: str
):
    """Test searching candidates by name (case-insensitive)."""
    candidate1 = create_candidate(name="John Doe", status=CandidateStatus.ACTIVE)
    candidate2 = create_candidate(name="Jane Smith", status=CandidateStatus.ACTIVE)
    candidate3 = create_candidate(name="Bob Johnson", status=CandidateStatus.ACTIVE)

    db_session.add_all([candidate1, candidate2, candidate3])
    await db_session.commit()

    # Search for "john" - should match "John Doe" and "Bob Johnson"
    response = await client.get(
        "/api/v1/candidates?search=john",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    names = {c["name"] for c in data["candidates"]}
    assert "John Doe" in names
    assert "Bob Johnson" in names


@pytest.mark.asyncio
async def test_search_candidates_by_email(
    client: AsyncClient, db_session: AsyncSession, auth_token: str
):
    """Test searching candidates by email."""
    candidate = create_candidate(
        name="Test User",
        email="specific@example.com",
        status=CandidateStatus.ACTIVE
    )
    db_session.add(candidate)
    await db_session.commit()

    response = await client.get(
        "/api/v1/candidates?search=specific",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["candidates"][0]["email"] == "specific@example.com"


@pytest.mark.asyncio
async def test_search_candidates_by_skill(
    client: AsyncClient, db_session: AsyncSession, auth_token: str
):
    """Test searching candidates by skill name."""
    candidate1 = create_candidate(name="Python Dev", status=CandidateStatus.ACTIVE)
    candidate2 = create_candidate(name="Java Dev", status=CandidateStatus.ACTIVE)

    db_session.add_all([candidate1, candidate2])
    await db_session.flush()

    # Add skills
    skill1 = create_skill(candidate1.id, name="Python", level=SkillLevel.EXPERT)
    skill2 = create_skill(candidate2.id, name="Java", level=SkillLevel.ADVANCED)

    db_session.add_all([skill1, skill2])
    await db_session.commit()

    # Search for "python"
    response = await client.get(
        "/api/v1/candidates?search=python",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["candidates"][0]["name"] == "Python Dev"


@pytest.mark.asyncio
async def test_filter_candidates_by_position(
    client: AsyncClient, db_session: AsyncSession, auth_token: str
):
    """Test filtering candidates by position."""
    candidate1 = create_candidate(name="Candidate 1", status=CandidateStatus.ACTIVE)
    candidate2 = create_candidate(name="Candidate 2", status=CandidateStatus.ACTIVE)
    position = create_position(title="Senior Developer")

    db_session.add_all([candidate1, candidate2, position])
    await db_session.flush()

    # Link candidate1 to position
    link = CandidatePosition(candidate_id=candidate1.id, position_id=position.id)
    db_session.add(link)
    await db_session.commit()

    # Filter by position
    response = await client.get(
        f"/api/v1/candidates?positionId={position.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["candidates"][0]["name"] == "Candidate 1"


@pytest.mark.asyncio
async def test_get_candidates_pagination(
    client: AsyncClient, db_session: AsyncSession, auth_token: str
):
    """Test pagination works correctly."""
    # Create 5 active candidates
    candidates = [
        create_candidate(name=f"Candidate {i}", status=CandidateStatus.ACTIVE)
        for i in range(5)
    ]
    db_session.add_all(candidates)
    await db_session.commit()

    # Get first 2
    response = await client.get(
        "/api/v1/candidates?limit=2&offset=0",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["candidates"]) == 2
    assert data["total"] == 5

    # Get next 2
    response = await client.get(
        "/api/v1/candidates?limit=2&offset=2",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["candidates"]) == 2
    assert data["total"] == 5


@pytest.mark.asyncio
async def test_get_candidate_by_id_success(
    client: AsyncClient, db_session: AsyncSession, auth_token: str
):
    """Test getting a single candidate by ID."""
    candidate = create_candidate(
        name="John Doe",
        email="john@example.com",
        status=CandidateStatus.ACTIVE
    )
    db_session.add(candidate)
    await db_session.flush()

    # Add experience, education, skills, documents
    experience = create_experience(
        candidate.id,
        company="Tech Corp",
        title="Developer",
        start_date=date(2020, 1, 1),
        end_date=None,  # Current job
    )
    education = create_education(
        candidate.id,
        institution="MIT",
        degree="BS Computer Science",
    )
    skill = create_skill(candidate.id, name="Python", level=SkillLevel.EXPERT)
    document = create_document(candidate.id, name="resume.pdf")

    db_session.add_all([experience, education, skill, document])
    await db_session.commit()

    response = await client.get(
        f"/api/v1/candidates/{candidate.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == candidate.id
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert len(data["experience"]) == 1
    assert len(data["education"]) == 1
    assert len(data["skills"]) == 1
    assert len(data["documents"]) == 1


@pytest.mark.asyncio
async def test_get_candidate_by_id_not_found(client: AsyncClient, auth_token: str):
    """Test getting non-existent candidate returns 404."""
    response = await client.get(
        "/api/v1/candidates/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_candidate_response_matches_contract(
    client: AsyncClient, db_session: AsyncSession, auth_token: str
):
    """Test that candidate response matches Exercise 1 JSON contract (camelCase)."""
    candidate = create_candidate(status=CandidateStatus.ACTIVE)
    db_session.add(candidate)
    await db_session.flush()

    skill = create_skill(candidate.id, name="Python", level=SkillLevel.EXPERT)
    db_session.add(skill)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/candidates/{candidate.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Check camelCase fields match Exercise 1 contract
    assert "id" in data
    assert "name" in data
    assert "email" in data
    assert "phone" in data
    assert "location" in data
    assert "summary" in data
    assert "experience" in data  # Array
    assert "education" in data  # Array
    assert "skills" in data  # Array
    assert "documents" in data  # Array
    assert "appliedPositions" in data  # Array of position IDs
    assert "status" in data
    assert "yearsOfExperience" in data  # Calculated field
    assert "sortOrder" in data

    # Check skill structure
    assert data["skills"][0]["name"] == "Python"
    assert data["skills"][0]["level"] == "Expert"
