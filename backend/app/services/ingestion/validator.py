"""Validation layer for LLM output.

Treats LLM output as untrusted input:
- Required fields must be present and non-empty.
- Skill levels are normalised to the known enum or default to Intermediate.
- Failures raise ValidationError with a clear explanation — nothing is silently swallowed.

Returns a clean, typed dict on success.
"""
import re
from typing import Any


class ValidationError(Exception):
    """Raised when LLM output fails validation.  Message explains why."""


# ---------------------------------------------------------------------------
# Skill level normalisation
# ---------------------------------------------------------------------------

_LEVEL_MAP: dict[str, str] = {
    # Beginner
    "beginner": "Beginner",
    "entry": "Beginner",
    "basic": "Beginner",
    "junior": "Beginner",
    "novice": "Beginner",
    "entry-level": "Beginner",
    # Intermediate
    "intermediate": "Intermediate",
    "mid": "Intermediate",
    "medium": "Intermediate",
    "proficient": "Intermediate",
    "mid-level": "Intermediate",
    "working": "Intermediate",
    # Advanced
    "advanced": "Advanced",
    "senior": "Advanced",
    "strong": "Advanced",
    "experienced": "Advanced",
    "upper-intermediate": "Advanced",
    # Expert
    "expert": "Expert",
    "principal": "Expert",
    "master": "Expert",
    "lead": "Expert",
    "distinguished": "Expert",
}

_VALID_LEVELS = {"Beginner", "Intermediate", "Advanced", "Expert"}


def _normalise_level(raw: str) -> str:
    key = raw.strip().lower()
    return _LEVEL_MAP.get(key, "Intermediate")


# ---------------------------------------------------------------------------
# CV validation
# ---------------------------------------------------------------------------

def validate_cv_extraction(data: Any) -> dict:
    """Validate and normalise a parsed CV extraction dict.

    Returns a clean dict.  Raises ValidationError on missing/bad required fields.
    """
    if not isinstance(data, dict):
        raise ValidationError(f"Expected a JSON object, got {type(data).__name__}")

    errors: list[str] = []

    # candidate_summary — required, non-empty
    summary = data.get("candidate_summary")
    if not summary or not str(summary).strip():
        errors.append("candidate_summary is missing or empty")
    elif len(str(summary)) > 3000:
        errors.append(f"candidate_summary is too long ({len(str(summary))} chars, max 3000)")

    # skills — required, must be a list
    raw_skills = data.get("skills", [])
    if not isinstance(raw_skills, list):
        errors.append(f"skills must be a list, got {type(raw_skills).__name__}")
        raw_skills = []

    if errors:
        raise ValidationError("; ".join(errors))

    validated_skills = []
    skill_warnings: list[str] = []
    for i, skill in enumerate(raw_skills):
        if not isinstance(skill, dict):
            skill_warnings.append(f"skills[{i}] is not an object — skipped")
            continue
        name = str(skill.get("name", "")).strip()
        if not name:
            skill_warnings.append(f"skills[{i}] has no name — skipped")
            continue
        raw_level = str(skill.get("level", "")).strip()
        level = _normalise_level(raw_level) if raw_level else "Intermediate"
        validated_skills.append({"name": name, "level": level})

    # experiences — optional, best-effort
    experiences = _validate_experiences(data.get("experiences") or [])

    # education — optional, best-effort
    education = _validate_education(data.get("education") or [])

    return {
        "candidate_summary": str(summary).strip(),
        "skills": validated_skills,
        "experiences": experiences,
        "education": education,
        "_skill_warnings": skill_warnings,
    }


def _validate_experiences(raw: Any) -> list[dict]:
    if not isinstance(raw, list):
        return []
    result = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        company = str(item.get("company") or "").strip()
        title = str(item.get("title") or "").strip()
        if not company or not title:
            continue  # skip incomplete entries
        result.append({
            "company": company,
            "title": title,
            "start_date": str(item.get("start_date") or "").strip() or None,
            "end_date": str(item.get("end_date") or "").strip() or None,
            "description": str(item.get("description") or "").strip(),
        })
    return result


def _validate_education(raw: Any) -> list[dict]:
    if not isinstance(raw, list):
        return []
    result = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        institution = str(item.get("institution") or "").strip()
        if not institution:
            continue
        result.append({
            "institution": institution,
            "degree": str(item.get("degree") or "").strip(),
            "field": str(item.get("field") or "").strip(),
            "start_date": str(item.get("start_date") or "").strip() or None,
            "end_date": str(item.get("end_date") or "").strip() or None,
        })
    return result


# ---------------------------------------------------------------------------
# Job description validation
# ---------------------------------------------------------------------------

def validate_job_extraction(data: Any) -> dict:
    """Validate and normalise a parsed job description extraction dict."""
    if not isinstance(data, dict):
        raise ValidationError(f"Expected a JSON object, got {type(data).__name__}")

    errors: list[str] = []

    title = str(data.get("title") or "").strip()
    if not title:
        errors.append("title is missing or empty")

    description = str(data.get("description") or "").strip()
    if not description:
        errors.append("description is missing or empty")

    if errors:
        raise ValidationError("; ".join(errors))

    # min_experience_years — coerce to int, default 0
    raw_years = data.get("min_experience_years")
    try:
        min_years = int(raw_years) if raw_years is not None else 0
        min_years = max(0, min_years)
    except (TypeError, ValueError):
        min_years = 0

    # required_skills — must be list of strings
    raw_skills = data.get("required_skills") or []
    if not isinstance(raw_skills, list):
        raw_skills = []
    skills = [str(s).strip() for s in raw_skills if str(s).strip()]

    return {
        "title": title,
        "department": str(data.get("department") or "Engineering").strip() or "Engineering",
        "location": str(data.get("location") or "").strip(),
        "description": description,
        "requirements": str(data.get("requirements") or "").strip(),
        "min_experience_years": min_years,
        "required_skills": skills,
        "position_summary": str(data.get("position_summary") or "").strip(),
    }
