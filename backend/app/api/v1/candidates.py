"""Candidates API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, require_editor
from app.db.session import get_db
from app.models.candidate import CandidateStatus
from app.repositories.candidate import CandidateRepository
from app.repositories.candidate_position import CandidatePositionRepository
from app.schemas.candidate import (
    CandidateDetail,
    CandidateListItem,
    CandidateListResponse,
    DocumentSchema,
    EducationSchema,
    ExperienceSchema,
    SkillSchema,
)
from app.services.candidate import CandidateService

router = APIRouter()


@router.get("", response_model=CandidateListResponse)
async def list_candidates(
    status: Optional[CandidateStatus] = Query(CandidateStatus.ACTIVE),
    search: Optional[str] = Query(None),
    position_id: Optional[str] = Query(None, alias="positionId"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """
    List candidates with filters and pagination.

    - **status**: Filter by candidate status (default: Active)
    - **search**: Search by name, email, or skill (case-insensitive)
    - **positionId**: Filter candidates who applied to this position
    - **limit**: Maximum number of results (default: 100)
    - **offset**: Number of results to skip (default: 0)
    """
    candidates, total = await CandidateRepository.get_candidates(
        db=db,
        status=status,
        search=search,
        position_id=position_id,
        limit=limit,
        offset=offset,
    )

    # Convert to response format
    candidate_list = []
    for candidate in candidates:
        # Calculate years of experience
        years_exp = CandidateService.calculate_years_of_experience(candidate.experiences)

        # Get applied position IDs
        applied_positions = [cp.position_id for cp in candidate.candidate_positions]

        # Convert skills
        skills = [
            SkillSchema(name=s.name, level=s.level)
            for s in candidate.skills
        ]

        candidate_item = CandidateListItem(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            location=candidate.location,
            summary=candidate.summary,
            status=candidate.status,
            years_of_experience=years_exp,
            sort_order=candidate.sort_order,
            skills=skills,
            applied_positions=applied_positions,
        )
        candidate_list.append(candidate_item)

    return CandidateListResponse(candidates=candidate_list, total=total)


@router.get("/{candidate_id}", response_model=CandidateDetail)
async def get_candidate(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """Get a single candidate by ID with full details."""
    candidate = await CandidateRepository.get_candidate_by_id(db, candidate_id)

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Calculate years of experience
    years_exp = CandidateService.calculate_years_of_experience(candidate.experiences)

    # Get applied position IDs
    applied_positions = [cp.position_id for cp in candidate.candidate_positions]

    # Convert nested data
    experience = [
        ExperienceSchema(
            company=e.company,
            title=e.title,
            start_date=e.start_date,
            end_date=e.end_date,
            description=e.description,
        )
        for e in candidate.experiences
    ]

    education = [
        EducationSchema(
            institution=ed.institution,
            degree=ed.degree,
            field=ed.field,
            start_date=ed.start_date,
            end_date=ed.end_date,
        )
        for ed in candidate.education
    ]

    skills = [
        SkillSchema(name=s.name, level=s.level)
        for s in candidate.skills
    ]

    documents = [
        DocumentSchema(type=d.type, name=d.name, url=d.url)
        for d in candidate.documents
    ]

    return CandidateDetail(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        location=candidate.location,
        summary=candidate.summary,
        status=candidate.status,
        years_of_experience=years_exp,
        sort_order=candidate.sort_order,
        experience=experience,
        education=education,
        skills=skills,
        documents=documents,
        applied_positions=applied_positions,
    )


@router.post("/{candidate_id}/positions/{position_id}", status_code=201)
async def add_position_to_candidate(
    candidate_id: str,
    position_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_editor),
):
    """
    Add a position to a candidate (candidate applies to position).

    Requires editor or admin role.
    """
    try:
        await CandidatePositionRepository.add_position_to_candidate(
            db, candidate_id, position_id
        )
        return {"message": "Position added to candidate"}
    except ValueError as e:
        error_msg = str(e).lower()
        if "candidate not found" in error_msg:
            raise HTTPException(status_code=404, detail="Candidate not found")
        elif "position not found" in error_msg:
            raise HTTPException(status_code=404, detail="Position not found")
        elif "already applied" in error_msg:
            raise HTTPException(
                status_code=409,
                detail="Candidate has already applied to this position",
            )
        else:
            raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{candidate_id}/positions/{position_id}")
async def remove_position_from_candidate(
    candidate_id: str,
    position_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_editor),
):
    """
    Remove a position from a candidate.

    Requires editor or admin role.
    """
    removed = await CandidatePositionRepository.remove_position_from_candidate(
        db, candidate_id, position_id
    )

    if not removed:
        raise HTTPException(
            status_code=404,
            detail="Relationship not found",
        )

    return {"message": "Position removed from candidate"}
