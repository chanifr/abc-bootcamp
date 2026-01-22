"""API tests for authentication endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.core.security import hash_password


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    """Test successful login."""
    # Create a user
    user = User(
        email="test@example.com",
        hashed_password=hash_password("password123"),
        full_name="Test User",
        role=UserRole.EDITOR,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    # Attempt login
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20
    assert len(data["refresh_token"]) > 20


@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient):
    """Test login with non-existent email."""
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, db_session: AsyncSession):
    """Test login with incorrect password."""
    # Create a user
    user = User(
        email="test@example.com",
        hashed_password=hash_password("correctpassword"),
        full_name="Test User",
        role=UserRole.EDITOR,
    )
    db_session.add(user)
    await db_session.commit()

    # Attempt login with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient, db_session: AsyncSession):
    """Test that inactive users cannot login."""
    # Create an inactive user
    user = User(
        email="inactive@example.com",
        hashed_password=hash_password("password123"),
        full_name="Inactive User",
        role=UserRole.READ_ONLY,
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()

    # Attempt login
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "inactive@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Inactive user"


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, db_session: AsyncSession):
    """Test getting current user info with valid token."""
    # Create a user
    user = User(
        email="current@example.com",
        hashed_password=hash_password("password123"),
        full_name="Current User",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    await db_session.commit()

    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "current@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"
    assert data["full_name"] == "Current User"
    assert data["role"] == "admin"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """Test getting current user without token returns 401."""
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token returns 401."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, db_session: AsyncSession):
    """Test refreshing access token with refresh token."""
    # Create a user
    user = User(
        email="refresh@example.com",
        hashed_password=hash_password("password123"),
        full_name="Refresh User",
        role=UserRole.EDITOR,
    )
    db_session.add(user)
    await db_session.commit()

    # Login to get tokens
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "refresh@example.com", "password": "password123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh access token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20
