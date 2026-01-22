"""API tests for candidate-position relationship endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.candidate_position import CandidatePosition
from app.models.user import User, UserRole
from tests.fixtures.factories import create_candidate, create_position


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
async def test_add_position_to_candidate_requires_editor(
    client: AsyncClient, db_session: AsyncSession, read_only_token: str
):
    """Test that read-only users cannot add position to candidate."""
    candidate = create_candidate()
    position = create_position()
    db_session.add_all([candidate, position])
    await db_session.commit()

    response = await client.post(
        f"/api/v1/candidates/{candidate.id}/positions/{position.id}",
        headers={"Authorization": f"Bearer {read_only_token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_position_to_candidate_success(
    client: AsyncClient, db_session: AsyncSession, editor_token: str
):
    """Test successfully adding a position to a candidate."""
    candidate = create_candidate()
    position = create_position()
    db_session.add_all([candidate, position])
    await db_session.commit()

    response = await client.post(
        f"/api/v1/candidates/{candidate.id}/positions/{position.id}",
        headers={"Authorization": f"Bearer {editor_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Position added to candidate"

    # Verify relationship was created in database
    result = await db_session.execute(
        select(CandidatePosition).where(
            CandidatePosition.candidate_id == candidate.id,
            CandidatePosition.position_id == position.id,
        )
    )
    link = result.scalar_one_or_none()
    assert link is not None


@pytest.mark.asyncio
async def test_add_position_already_exists(
    client: AsyncClient, db_session: AsyncSession, editor_token: str
):
    """Test adding a position that's already linked returns 409."""
    candidate = create_candidate()
    position = create_position()
    db_session.add_all([candidate, position])
    await db_session.flush()

    # Create existing relationship
    link = CandidatePosition(candidate_id=candidate.id, position_id=position.id)
    db_session.add(link)
    await db_session.commit()

    # Try to add again
    response = await client.post(
        f"/api/v1/candidates/{candidate.id}/positions/{position.id}",
        headers={"Authorization": f"Bearer {editor_token}"},
    )

    assert response.status_code == 409
    assert "already applied" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_position_candidate_not_found(
    client: AsyncClient, db_session: AsyncSession, editor_token: str
):
    """Test adding position to non-existent candidate returns 404."""
    position = create_position()
    db_session.add(position)
    await db_session.commit()

    response = await client.post(
        f"/api/v1/candidates/00000000-0000-0000-0000-000000000000/positions/{position.id}",
        headers={"Authorization": f"Bearer {editor_token}"},
    )

    assert response.status_code == 404
    assert "candidate" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_position_position_not_found(
    client: AsyncClient, db_session: AsyncSession, editor_token: str
):
    """Test adding non-existent position to candidate returns 404."""
    candidate = create_candidate()
    db_session.add(candidate)
    await db_session.commit()

    response = await client.post(
        f"/api/v1/candidates/{candidate.id}/positions/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {editor_token}"},
    )

    assert response.status_code == 404
    assert "position" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_remove_position_from_candidate(
    client: AsyncClient, db_session: AsyncSession, editor_token: str
):
    """Test successfully removing a position from a candidate."""
    candidate = create_candidate()
    position = create_position()
    db_session.add_all([candidate, position])
    await db_session.flush()

    # Create relationship
    link = CandidatePosition(candidate_id=candidate.id, position_id=position.id)
    db_session.add(link)
    await db_session.commit()

    response = await client.delete(
        f"/api/v1/candidates/{candidate.id}/positions/{position.id}",
        headers={"Authorization": f"Bearer {editor_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Position removed from candidate"

    # Verify relationship was deleted
    result = await db_session.execute(
        select(CandidatePosition).where(
            CandidatePosition.candidate_id == candidate.id,
            CandidatePosition.position_id == position.id,
        )
    )
    link = result.scalar_one_or_none()
    assert link is None


@pytest.mark.asyncio
async def test_remove_position_not_found(
    client: AsyncClient, db_session: AsyncSession, editor_token: str
):
    """Test removing non-existent relationship returns 404."""
    candidate = create_candidate()
    position = create_position()
    db_session.add_all([candidate, position])
    await db_session.commit()

    # No relationship created

    response = await client.delete(
        f"/api/v1/candidates/{candidate.id}/positions/{position.id}",
        headers={"Authorization": f"Bearer {editor_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_remove_position_requires_editor(
    client: AsyncClient, db_session: AsyncSession, read_only_token: str
):
    """Test that read-only users cannot remove position from candidate."""
    candidate = create_candidate()
    position = create_position()
    db_session.add_all([candidate, position])
    await db_session.flush()

    link = CandidatePosition(candidate_id=candidate.id, position_id=position.id)
    db_session.add(link)
    await db_session.commit()

    response = await client.delete(
        f"/api/v1/candidates/{candidate.id}/positions/{position.id}",
        headers={"Authorization": f"Bearer {read_only_token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_candidate_response_includes_positions(
    client: AsyncClient, db_session: AsyncSession, editor_token: str
):
    """Test that candidate response includes appliedPositions array."""
    candidate = create_candidate()
    position1 = create_position(title="Position 1")
    position2 = create_position(title="Position 2")
    db_session.add_all([candidate, position1, position2])
    await db_session.flush()

    # Add candidate to positions
    link1 = CandidatePosition(candidate_id=candidate.id, position_id=position1.id)
    link2 = CandidatePosition(candidate_id=candidate.id, position_id=position2.id)
    db_session.add_all([link1, link2])
    await db_session.commit()

    # Get candidate
    response = await client.get(
        f"/api/v1/candidates/{candidate.id}",
        headers={"Authorization": f"Bearer {editor_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "appliedPositions" in data
    assert len(data["appliedPositions"]) == 2
    assert position1.id in data["appliedPositions"]
    assert position2.id in data["appliedPositions"]


@pytest.mark.asyncio
async def test_position_response_includes_candidates(
    client: AsyncClient, db_session: AsyncSession, editor_token: str
):
    """Test that position response includes candidates array."""
    candidate1 = create_candidate(name="Candidate 1")
    candidate2 = create_candidate(name="Candidate 2")
    position = create_position()
    db_session.add_all([candidate1, candidate2, position])
    await db_session.flush()

    # Add candidates to position
    link1 = CandidatePosition(candidate_id=candidate1.id, position_id=position.id)
    link2 = CandidatePosition(candidate_id=candidate2.id, position_id=position.id)
    db_session.add_all([link1, link2])
    await db_session.commit()

    # Get position
    response = await client.get(
        f"/api/v1/positions/{position.id}",
        headers={"Authorization": f"Bearer {editor_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data
    assert len(data["candidates"]) == 2
    assert candidate1.id in data["candidates"]
    assert candidate2.id in data["candidates"]
