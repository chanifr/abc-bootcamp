#!/usr/bin/env python3
"""Create default admin user for development."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole


async def create_admin_user():
    """Create admin user if it doesn't exist."""
    async with AsyncSessionLocal() as session:
        # Check if admin user already exists
        result = await session.execute(
            select(User).where(User.email == "admin@hellio.com")
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("Admin user already exists!")
            print(f"  Email: {existing_user.email}")
            print(f"  Role: {existing_user.role.value}")
            return

        # Create admin user
        admin_user = User(
            email="admin@hellio.com",
            hashed_password=hash_password("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
        )

        session.add(admin_user)
        await session.commit()

        print("Admin user created successfully!")
        print("  Email: admin@hellio.com")
        print("  Password: admin123")
        print("  Role: admin")
        print("\nIMPORTANT: Change the password in production!")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
