"""Position repository for database operations."""

from typing import Optional

from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.position import Position, PositionStatus
from app.models.position_skill import PositionSkill


class PositionRepository:
    """Data access layer for positions."""

    @staticmethod
    async def get_positions(
        db: AsyncSession,
        status: Optional[PositionStatus] = PositionStatus.OPEN,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Position], int]:
        """
        Get positions with filters and pagination.

        Returns tuple of (positions, total_count).
        """
        # Base query
        query = select(Position).options(
            selectinload(Position.required_skills),
            selectinload(Position.candidate_positions),
        )

        # Filter by status
        if status:
            query = query.where(Position.status == status)

        # Search by title, department, or location
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Position.title.ilike(search_term),
                    Position.department.ilike(search_term),
                    Position.location.ilike(search_term),
                )
            )

        # Get total count (before pagination)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Position.sort_order, Position.title)
        query = query.limit(limit).offset(offset)

        # Execute query
        result = await db.execute(query)
        positions = result.scalars().all()

        return list(positions), total

    @staticmethod
    async def get_position_by_id(
        db: AsyncSession,
        position_id: str,
    ) -> Optional[Position]:
        """Get a single position by ID with all related data."""
        query = (
            select(Position)
            .where(Position.id == position_id)
            .options(
                selectinload(Position.required_skills),
                selectinload(Position.candidate_positions),
            )
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_position(
        db: AsyncSession,
        position: Position,
        title: str,
        department: str,
        location: str,
        description: str,
        requirements: str,
        min_experience_years: int,
        status: PositionStatus,
        posted_date,
        required_skills: list[str],
    ) -> Position:
        """Update a position and its required skills."""
        # Update position fields
        position.title = title
        position.department = department
        position.location = location
        position.description = description
        position.requirements = requirements
        position.min_experience_years = min_experience_years
        position.status = status
        position.posted_date = posted_date

        # Update required skills - delete old ones and add new ones
        # Delete existing skills
        for skill in position.required_skills:
            await db.delete(skill)

        await db.flush()

        # Add new skills
        for skill_name in required_skills:
            new_skill = PositionSkill(position_id=position.id, name=skill_name)
            db.add(new_skill)

        await db.commit()
        await db.refresh(position)

        return position
