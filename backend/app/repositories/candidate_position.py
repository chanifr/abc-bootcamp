"""Candidate-Position relationship repository."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.models.candidate_position import CandidatePosition
from app.models.position import Position


class CandidatePositionRepository:
    """Data access layer for candidate-position relationships."""

    @staticmethod
    async def add_position_to_candidate(
        db: AsyncSession,
        candidate_id: str,
        position_id: str,
    ) -> CandidatePosition:
        """
        Add a position to a candidate (candidate applies to position).

        Raises ValueError if relationship already exists.
        Raises ValueError if candidate or position not found.
        """
        # Verify candidate exists
        candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = candidate_result.scalar_one_or_none()
        if not candidate:
            raise ValueError("Candidate not found")

        # Verify position exists
        position_result = await db.execute(
            select(Position).where(Position.id == position_id)
        )
        position = position_result.scalar_one_or_none()
        if not position:
            raise ValueError("Position not found")

        # Check if relationship already exists
        existing = await db.execute(
            select(CandidatePosition).where(
                CandidatePosition.candidate_id == candidate_id,
                CandidatePosition.position_id == position_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Candidate has already applied to this position")

        # Create relationship
        link = CandidatePosition(candidate_id=candidate_id, position_id=position_id)
        db.add(link)

        try:
            await db.commit()
            await db.refresh(link)
            return link
        except IntegrityError:
            await db.rollback()
            raise ValueError("Failed to create relationship")

    @staticmethod
    async def remove_position_from_candidate(
        db: AsyncSession,
        candidate_id: str,
        position_id: str,
    ) -> bool:
        """
        Remove a position from a candidate.

        Returns True if removed, False if relationship didn't exist.
        """
        result = await db.execute(
            select(CandidatePosition).where(
                CandidatePosition.candidate_id == candidate_id,
                CandidatePosition.position_id == position_id,
            )
        )
        link = result.scalar_one_or_none()

        if not link:
            return False

        await db.delete(link)
        await db.commit()
        return True

    @staticmethod
    async def get_relationship(
        db: AsyncSession,
        candidate_id: str,
        position_id: str,
    ) -> Optional[CandidatePosition]:
        """Get a specific candidate-position relationship."""
        result = await db.execute(
            select(CandidatePosition).where(
                CandidatePosition.candidate_id == candidate_id,
                CandidatePosition.position_id == position_id,
            )
        )
        return result.scalar_one_or_none()
