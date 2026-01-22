"""Positions API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_editor
from app.db.session import get_db
from app.models.position import PositionStatus
from app.repositories.position import PositionRepository
from app.schemas.position import (
    PositionDetail,
    PositionListItem,
    PositionListResponse,
    PositionUpdate,
)

router = APIRouter()


@router.get("", response_model=PositionListResponse)
async def list_positions(
    status: Optional[PositionStatus] = Query(PositionStatus.OPEN),
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    List positions with filters and pagination.

    - **status**: Filter by position status (default: Open)
    - **search**: Search by title, department, or location (case-insensitive)
    - **limit**: Maximum number of results (default: 100)
    - **offset**: Number of results to skip (default: 0)
    """
    positions, total = await PositionRepository.get_positions(
        db=db,
        status=status,
        search=search,
        limit=limit,
        offset=offset,
    )

    # Convert to response format
    position_list = []
    for position in positions:
        # Get required skill names
        required_skills = [skill.name for skill in position.required_skills]

        # Get candidate IDs
        candidate_ids = [cp.candidate_id for cp in position.candidate_positions]

        position_item = PositionListItem(
            id=position.id,
            title=position.title,
            department=position.department,
            location=position.location,
            description=position.description,
            requirements=position.requirements,
            required_skills=required_skills,
            min_experience_years=position.min_experience_years,
            status=position.status,
            posted_date=position.posted_date,
            candidates=candidate_ids,
            sort_order=position.sort_order,
        )
        position_list.append(position_item)

    return PositionListResponse(positions=position_list, total=total)


@router.get("/{position_id}", response_model=PositionDetail)
async def get_position(
    position_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Get a single position by ID with full details."""
    position = await PositionRepository.get_position_by_id(db, position_id)

    if not position:
        raise HTTPException(status_code=404, detail="Position not found")

    # Get required skill names
    required_skills = [skill.name for skill in position.required_skills]

    # Get candidate IDs
    candidate_ids = [cp.candidate_id for cp in position.candidate_positions]

    return PositionDetail(
        id=position.id,
        title=position.title,
        department=position.department,
        location=position.location,
        description=position.description,
        requirements=position.requirements,
        required_skills=required_skills,
        min_experience_years=position.min_experience_years,
        status=position.status,
        posted_date=position.posted_date,
        candidates=candidate_ids,
        sort_order=position.sort_order,
    )


@router.put("/{position_id}", response_model=PositionDetail)
async def update_position(
    position_id: str,
    position_data: PositionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_editor),
):
    """
    Update a position (requires editor or admin role).

    Updates all position fields including required skills.
    """
    position = await PositionRepository.get_position_by_id(db, position_id)

    if not position:
        raise HTTPException(status_code=404, detail="Position not found")

    # Update position
    updated_position = await PositionRepository.update_position(
        db=db,
        position=position,
        title=position_data.title,
        department=position_data.department,
        location=position_data.location,
        description=position_data.description,
        requirements=position_data.requirements,
        min_experience_years=position_data.min_experience_years,
        status=position_data.status,
        posted_date=position_data.posted_date,
        required_skills=position_data.required_skills,
    )

    # Reload to get updated skills
    await db.refresh(updated_position)
    position = await PositionRepository.get_position_by_id(db, position_id)

    # Get required skill names
    required_skills = [skill.name for skill in position.required_skills]

    # Get candidate IDs
    candidate_ids = [cp.candidate_id for cp in position.candidate_positions]

    return PositionDetail(
        id=position.id,
        title=position.title,
        department=position.department,
        location=position.location,
        description=position.description,
        requirements=position.requirements,
        required_skills=required_skills,
        min_experience_years=position.min_experience_years,
        status=position.status,
        posted_date=position.posted_date,
        candidates=candidate_ids,
        sort_order=position.sort_order,
    )
