"""Persistence layer — writes validated extraction output to the existing schema.

Strategy:
  CV:   upsert Candidate by email (update if exists, create if not).
        Re-create Skills on every run so they reflect the latest extraction.
        Add Experience and Education rows from LLM output (best-effort).
  Job:  upsert Position by (title, department) pair.
        Re-create PositionSkill on every run.

Raises PersistenceError when required identifiers are missing so the
pipeline can mark the ingestion as failed rather than silently skip.
"""
import logging
import re
from datetime import date
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate, CandidateStatus
from app.models.document import Document, DocumentType
from app.models.education import Education
from app.models.experience import Experience
from app.models.position import Position, PositionStatus
from app.models.position_skill import PositionSkill
from app.models.skill import Skill, SkillLevel

logger = logging.getLogger(__name__)


class PersistenceError(Exception):
    """Raised when required data is absent and the record cannot be saved."""


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _parse_partial_date(value: str | None) -> date | None:
    """Parse YYYY-MM, YYYY-MM-DD, or YYYY strings into a date.

    Returns None for missing/unparseable values without raising.
    """
    if not value:
        return None
    value = value.strip()
    patterns = [
        (r"^(\d{4})-(\d{2})-(\d{2})$", lambda m: date(int(m[0]), int(m[1]), int(m[2]))),
        (r"^(\d{4})-(\d{2})$",          lambda m: date(int(m[0]), int(m[1]), 1)),
        (r"^(\d{4})$",                   lambda m: date(int(m[0]), 1, 1)),
    ]
    for pattern, builder in patterns:
        m = re.match(pattern, value)
        if m:
            try:
                return builder(m.groups())
            except ValueError:
                return None
    return None


# ---------------------------------------------------------------------------
# CV persistence
# ---------------------------------------------------------------------------

async def persist_candidate(
    session: AsyncSession,
    source_path: str,
    heuristic: dict[str, Any],
    llm_validated: dict[str, Any],
) -> tuple[Candidate, str]:
    """Upsert a Candidate row.  Returns (candidate, action) where action is
    'created' or 'updated'.

    Raises PersistenceError if no email is available (email is the only
    reliable unique identifier for upsert without a separate ID scheme).
    """
    email = heuristic.get("email", "").strip().lower()
    if not email:
        raise PersistenceError(
            "No email address extracted — cannot safely upsert candidate "
            "(email is the unique identifier)."
        )

    result = await session.execute(select(Candidate).where(Candidate.email == email))
    candidate = result.scalar_one_or_none()

    name = heuristic.get("name", "").strip() or "Unknown"
    phone = heuristic.get("phone", "").strip()
    location = heuristic.get("location", "").strip()
    summary = llm_validated.get("candidate_summary", "").strip()

    if candidate:
        # Update mutable fields; never overwrite with empty strings
        if name and name != "Unknown":
            candidate.name = name
        if phone:
            candidate.phone = phone
        if location:
            candidate.location = location
        if summary:
            candidate.summary = summary
        action = "updated"
        logger.info("Updated existing candidate: %s (%s)", candidate.name, email)
    else:
        candidate = Candidate(
            name=name,
            email=email,
            phone=phone or "",
            location=location or "",
            summary=summary or "",
            status=CandidateStatus.ACTIVE,
        )
        session.add(candidate)
        await session.flush()  # populate id
        action = "created"
        logger.info("Created new candidate: %s (%s)", name, email)

    # Re-create skills on every run (reflects current extraction)
    await session.execute(delete(Skill).where(Skill.candidate_id == candidate.id))
    for skill_data in llm_validated.get("skills", []):
        try:
            level = SkillLevel(skill_data["level"])
        except ValueError:
            level = SkillLevel.INTERMEDIATE
        session.add(Skill(
            candidate_id=candidate.id,
            name=skill_data["name"],
            level=level,
        ))

    # Add experiences (best-effort, never overwrite on update to avoid duplicates)
    if action == "created":
        _add_experiences(session, candidate.id, llm_validated.get("experiences", []))
        _add_education(session, candidate.id, llm_validated.get("education", []))

    # Record the source document
    session.add(Document(
        candidate_id=candidate.id,
        type=DocumentType.CV,
        name=source_path.split("/")[-1],
        url=source_path,
    ))

    return candidate, action


def _add_experiences(session: AsyncSession, candidate_id: str, experiences: list[dict]) -> None:
    for exp in experiences:
        start = _parse_partial_date(exp.get("start_date"))
        if not start:
            logger.warning("Skipping experience with unparseable start_date: %s", exp)
            continue
        session.add(Experience(
            candidate_id=candidate_id,
            company=exp["company"],
            title=exp["title"],
            start_date=start,
            end_date=_parse_partial_date(exp.get("end_date")),
            description=exp.get("description", ""),
        ))


def _add_education(session: AsyncSession, candidate_id: str, education: list[dict]) -> None:
    for edu in education:
        start = _parse_partial_date(edu.get("start_date"))
        if not start:
            logger.warning("Skipping education with unparseable start_date: %s", edu)
            continue
        session.add(Education(
            candidate_id=candidate_id,
            institution=edu["institution"],
            degree=edu.get("degree", ""),
            field=edu.get("field", ""),
            start_date=start,
            end_date=_parse_partial_date(edu.get("end_date")),
        ))


# ---------------------------------------------------------------------------
# Job persistence
# ---------------------------------------------------------------------------

async def persist_position(
    session: AsyncSession,
    heuristic: dict[str, Any],
    llm_validated: dict[str, Any],
) -> tuple[Position, str]:
    """Upsert a Position row.  Returns (position, action)."""
    title = llm_validated.get("title", "").strip()
    if not title:
        raise PersistenceError("No title extracted — cannot persist position.")

    department = llm_validated.get("department", "Engineering").strip() or "Engineering"

    result = await session.execute(
        select(Position).where(Position.title == title, Position.department == department)
    )
    position = result.scalar_one_or_none()

    location = llm_validated.get("location", "").strip() or heuristic.get("location", "").strip()
    description = llm_validated.get("description", "").strip()
    requirements = llm_validated.get("requirements", "").strip()
    min_years = llm_validated.get("min_experience_years", 0)

    if position:
        if description:
            position.description = description
        if requirements:
            position.requirements = requirements
        if location:
            position.location = location
        position.min_experience_years = min_years
        action = "updated"
        logger.info("Updated existing position: %s", title)
    else:
        position = Position(
            title=title,
            department=department,
            location=location or "",
            description=description or "",
            requirements=requirements or "",
            min_experience_years=min_years,
            status=PositionStatus.OPEN,
            posted_date=date.today(),
        )
        session.add(position)
        await session.flush()
        action = "created"
        logger.info("Created new position: %s", title)

    # Re-create required skills on every run
    await session.execute(delete(PositionSkill).where(PositionSkill.position_id == position.id))
    for skill_name in llm_validated.get("required_skills", []):
        session.add(PositionSkill(position_id=position.id, name=skill_name))

    return position, action
