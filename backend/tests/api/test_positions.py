"""API tests for positions endpoints."""

import pytest
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.candidate_position import CandidatePosition
from app.models.position import PositionStatus
from app.models.user import User, UserRole
from tests.fixtures.factories import (
    create_candidate,
    create_position,
    create_position_skill,
)


@pytest.fixture
async def read_only_token(client: AsyncClient, db_session: AsyncSession) -> str:
    """Create a read-only user and return auth token."""
    user = User(
        email="readonly@example.com",
        hashed_password=hash_password("password123"),
        full_name="Read Only User",
        role=UserRole.READ_ONLY,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "readonly@example.com", "password": "password123"},
    )
    return response.json()["access_token"]


@pytest.fixture
async def editor_token(client: AsyncClient, db_session: AsyncSession) -> str:
    """Create an editor user and return auth token."""
    user = User(
        email="editor@example.com",
        hashed_password=hash_password("password123"),
        full_name="Editor User",
        role=UserRole.EDITOR,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "editor@example.com", "password": "password123"},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_get_positions_requires_auth(client: AsyncClient):
    """Test that getting positions requires authentication."""
    response = await client.get("/api/v1/positions")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_positions_empty(client: AsyncClient, read_only_token: str):
    """Test getting positions when none exist."""
    response = await client.get(
        "/api/v1/positions",
        headers={"Authorization": f"Bearer {read_only_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["positions"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_positions_returns_open_only(
    client: AsyncClient, db_session: AsyncSession, read_only_token: str
):
    """Test that GET /positions returns only Open positions by default."""
    open_pos = create_position(title="Open Position", status=PositionStatus.OPEN)
    closed_pos = create_position(title="Closed Position", status=PositionStatus.CLOSED)

    db_session.add_all([open_pos, closed_pos])
    await db_session.commit()

    response = await client.get(
        "/api/v1/positions",
        headers={"Authorization": f"Bearer {read_only_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["positions"]) == 1
    assert data["positions"][0]["title"] == "Open Position"
    assert data["positions"][0]["status"] == "Open"


@pytest.mark.asyncio
async def test_get_positions_filter_by_status(
    client: AsyncClient, db_session: AsyncSession, read_only_token: str
):
    """Test filtering positions by status."""
    open_pos = create_position(title="Open", status=PositionStatus.OPEN)
    closed_pos = create_position(title="Closed", status=PositionStatus.CLOSED)

    db_session.add_all([open_pos, closed_pos])
    await db_session.commit()

    # Filter by Closed status
    response = await client.get(
        "/api/v1/positions?status=Closed",
        headers={"Authorization": f"Bearer {read_only_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["positions"][0]["title"] == "Closed"


@pytest.mark.asyncio
async def test_search_positions(
    client: AsyncClient, db_session: AsyncSession, read_only_token: str
):
    """Test searching positions by title, department, or location."""
    pos1 = create_position(title="Senior Developer", department="Engineering", status=PositionStatus.OPEN)
    pos2 = create_position(title="Designer", department="Design", status=PositionStatus.OPEN)

    db_session.add_all([pos1, pos2])
    await db_session.commit()

    # Search for "developer"
    response = await client.get(
        "/api/v1/positions?search=developer",
        headers={"Authorization": f"Bearer {read_only_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["positions"][0]["title"] == "Senior Developer"


@pytest.mark.asyncio
async def test_get_position_by_id(
    client: AsyncClient, db_session: AsyncSession, read_only_token: str
):
    """Test getting a single position by ID."""
    position = create_position(
        title="Senior Developer",
        department="Engineering",
        location="Remote",
        status=PositionStatus.OPEN,
    )
    db_session.add(position)
    await db_session.flush()

    # Add required skills
    skill1 = create_position_skill(position.id, name="Python")
    skill2 = create_position_skill(position.id, name="React")
    db_session.add_all([skill1, skill2])

    # Add candidate to position
    candidate = create_candidate()
    db_session.add(candidate)
    await db_session.flush()

    link = CandidatePosition(candidate_id=candidate.id, position_id=position.id)
    db_session.add(link)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/positions/{position.id}",
        headers={"Authorization": f"Bearer {read_only_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == position.id
    assert data["title"] == "Senior Developer"
    assert len(data["requiredSkills"]) == 2
    assert len(data["candidates"]) == 1


@pytest.mark.asyncio
async def test_get_position_by_id_not_found(client: AsyncClient, read_only_token: str):
    """Test getting non-existent position returns 404."""
    response = await client.get(
        "/api/v1/positions/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {read_only_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_position_requires_editor_role(
    client: AsyncClient, db_session: AsyncSession, read_only_token: str
):
    """Test that read-only users cannot update positions."""
    position = create_position(title="Developer", status=PositionStatus.OPEN)
    db_session.add(position)
    await db_session.commit()

    response = await client.put(
        f"/api/v1/positions/{position.id}",
        headers={"Authorization": f"Bearer {read_only_token}"},
        json={"title": "Senior Developer"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_position_success(
    client: AsyncClient, db_session: AsyncSession, editor_token: str
):
    """Test that editors can successfully update positions."""
    position = create_position(
        title="Developer",
        department="Engineering",
        location="Office",
        description="Original description",
        requirements="Original requirements",
        min_experience_years=3,
        status=PositionStatus.OPEN,
        posted_date=date(2024, 1, 1),
    )
    db_session.add(position)
    await db_session.flush()

    # Add existing skills
    skill = create_position_skill(position.id, name="Python")
    db_session.add(skill)
    await db_session.commit()

    # Update position
    update_data = {
        "title": "Senior Developer",
        "department": "Engineering",
        "location": "Remote",
        "description": "Updated description",
        "requirements": "Updated requirements",
        "minExperienceYears": 5,
        "status": "Open",
        "postedDate": "2024-01-15",
        "requiredSkills": ["Python", "JavaScript", "React"],
    }

    response = await client.put(
        f"/api/v1/positions/{position.id}",
        headers={"Authorization": f"Bearer {editor_token}"},
        json=update_data,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Senior Developer"
    assert data["location"] == "Remote"
    assert data["description"] == "Updated description"
    assert data["minExperienceYears"] == 5
    assert len(data["requiredSkills"]) == 3
    assert "JavaScript" in data["requiredSkills"]


@pytest.mark.asyncio
async def test_update_position_not_found(client: AsyncClient, editor_token: str):
    """Test updating non-existent position returns 404."""
    update_data = {
        "title": "Test Position",
        "department": "Engineering",
        "location": "Remote",
        "description": "Test description",
        "requirements": "Test requirements",
        "minExperienceYears": 3,
        "status": "Open",
        "postedDate": "2024-01-01",
        "requiredSkills": ["Python"],
    }
    response = await client.put(
        "/api/v1/positions/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {editor_token}"},
        json=update_data,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_position_validates_data(
    client: AsyncClient, db_session: AsyncSession, editor_token: str
):
    """Test that update validates required fields."""
    position = create_position()
    db_session.add(position)
    await db_session.commit()

    # Missing required fields
    response = await client.put(
        f"/api/v1/positions/{position.id}",
        headers={"Authorization": f"Bearer {editor_token}"},
        json={"title": ""},  # Empty title should fail
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_position_response_matches_contract(
    client: AsyncClient, db_session: AsyncSession, read_only_token: str
):
    """Test that position response matches Exercise 1 JSON contract (camelCase)."""
    position = create_position(status=PositionStatus.OPEN)
    db_session.add(position)
    await db_session.flush()

    skill = create_position_skill(position.id, name="Python")
    db_session.add(skill)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/positions/{position.id}",
        headers={"Authorization": f"Bearer {read_only_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Check camelCase fields match Exercise 1 contract
    assert "id" in data
    assert "title" in data
    assert "department" in data
    assert "location" in data
    assert "description" in data
    assert "requirements" in data
    assert "requiredSkills" in data  # Array of strings
    assert "minExperienceYears" in data
    assert "status" in data
    assert "postedDate" in data
    assert "candidates" in data  # Array of candidate IDs
    assert "sortOrder" in data
