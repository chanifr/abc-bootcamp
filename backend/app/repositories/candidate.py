"""Candidate repository for database operations."""

from typing import Optional

from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.candidate import Candidate, CandidateStatus
from app.models.candidate_position import CandidatePosition
from app.models.skill import Skill


class CandidateRepository:
    """Data access layer for candidates."""

    @staticmethod
    async def get_candidates(
        db: AsyncSession,
        status: Optional[CandidateStatus] = CandidateStatus.ACTIVE,
        search: Optional[str] = None,
        position_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Candidate], int]:
        """
        Get candidates with filters and pagination.

        Returns tuple of (candidates, total_count).
        """
        # Base query
        query = select(Candidate).options(
            selectinload(Candidate.experiences),
            selectinload(Candidate.skills),
            selectinload(Candidate.candidate_positions),
        )

        # Filter by status
        if status:
            query = query.where(Candidate.status == status)

        # Search by name, email, or skill
        if search:
            search_term = f"%{search}%"

            # Subquery for candidates with matching skills
            skill_subquery = (
                select(Skill.candidate_id)
                .where(Skill.name.ilike(search_term))
            )

            query = query.where(
                or_(
                    Candidate.name.ilike(search_term),
                    Candidate.email.ilike(search_term),
                    Candidate.id.in_(skill_subquery),
                )
            )

        # Filter by position
        if position_id:
            position_subquery = (
                select(CandidatePosition.candidate_id)
                .where(CandidatePosition.position_id == position_id)
            )
            query = query.where(Candidate.id.in_(position_subquery))

        # Get total count (before pagination)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Candidate.sort_order, Candidate.name)
        query = query.limit(limit).offset(offset)

        # Execute query
        result = await db.execute(query)
        candidates = result.scalars().all()

        return list(candidates), total

    @staticmethod
    async def get_candidate_by_id(
        db: AsyncSession,
        candidate_id: str,
    ) -> Optional[Candidate]:
        """Get a single candidate by ID with all related data."""
        query = (
            select(Candidate)
            .where(Candidate.id == candidate_id)
            .options(
                selectinload(Candidate.experiences),
                selectinload(Candidate.education),
                selectinload(Candidate.skills),
                selectinload(Candidate.documents),
                selectinload(Candidate.candidate_positions),
            )
        )

        result = await db.execute(query)
        return result.scalar_one_or_none()
