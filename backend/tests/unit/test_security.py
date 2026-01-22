"""Unit tests for security functions (password hashing, JWT tokens)."""

import pytest
from datetime import datetime, timedelta

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password():
    """Test password hashing."""
    password = "secret123"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 20
    assert hashed.startswith("$2b$")  # bcrypt hash prefix


def test_verify_password():
    """Test password verification."""
    password = "secret123"
    hashed = hash_password(password)

    # Correct password
    assert verify_password(password, hashed) is True

    # Incorrect password
    assert verify_password("wrong", hashed) is False
    assert verify_password("", hashed) is False


def test_create_access_token():
    """Test access token creation."""
    user_id = "user-123"
    token = create_access_token(user_id)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 20

    # Verify token can be decoded
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_refresh_token():
    """Test refresh token creation."""
    user_id = "user-456"
    token = create_refresh_token(user_id)

    assert token is not None
    assert isinstance(token, str)

    # Verify token can be decoded
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"


def test_decode_token_valid():
    """Test decoding a valid token."""
    user_id = "user-789"
    token = create_access_token(user_id)
    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["type"] == "access"


def test_decode_token_invalid():
    """Test decoding an invalid token."""
    invalid_token = "invalid.token.here"
    payload = decode_token(invalid_token)

    assert payload is None


def test_decode_token_expired():
    """Test decoding an expired token."""
    from jose import jwt
    from app.config import settings

    # Create an expired token
    expire = datetime.utcnow() - timedelta(minutes=10)
    payload = {
        "sub": "user-999",
        "type": "access",
        "exp": expire,
    }
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    result = decode_token(expired_token)
    assert result is None
