"""Deterministic, regex-based extraction.

Runs before any LLM call.  Results are stored as an artifact so fields can
always be attributed to their extraction method.

CV fields extracted here:  name, email, phone, location, section_headers
Job fields extracted here:  min_experience_years, location (heuristic guess)

Everything else goes to the LLM stage.
"""
import re
from typing import Any

# ---------------------------------------------------------------------------
# CV heuristics
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.I)

_PHONE_RE = re.compile(
    r"""
    (?:(?:\+|00)[1-9]\d{0,2}[\s\-.]?)?   # optional country code
    (?:\(?\d{2,4}\)?[\s\-.]?){1,3}        # area/local groups
    \d{4,}                                  # last group
    """,
    re.VERBOSE,
)

# City, State  /  City, Country — [^\n] prevents matching across lines
_LOCATION_RE = re.compile(
    r"\b([A-Z][a-zA-Z][a-zA-Z ']{0,30}),\s*([A-Z]{2}|[A-Z][a-zA-Z]{2,20})\b"
)

# Lines that look like section headers: ALL CAPS, possibly with colon/dash
_SECTION_HEADER_RE = re.compile(r"^([A-Z][A-Z\s&/\-]{2,}):?\s*$")

_KNOWN_HEADERS = {
    "EXPERIENCE", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "EMPLOYMENT",
    "EDUCATION", "ACADEMIC BACKGROUND",
    "SKILLS", "TECHNICAL SKILLS", "CORE COMPETENCIES", "COMPETENCIES",
    "CERTIFICATIONS", "CERTIFICATES", "AWARDS",
    "SUMMARY", "PROFILE", "OBJECTIVE", "ABOUT",
    "PROJECTS", "PUBLICATIONS", "LANGUAGES", "INTERESTS",
}


def extract_cv_heuristics(text: str) -> dict[str, Any]:
    """Return a dict with deterministically extracted CV fields."""
    lines = [l.rstrip() for l in text.splitlines()]
    non_blank = [l for l in lines if l.strip()]

    return {
        "name": _extract_name(non_blank),
        "email": _extract_email(text),
        "phone": _extract_phone(text),
        "location": _extract_location(text),
        "section_headers": _extract_section_headers(lines),
        "_source": "heuristic",
    }


_NAME_TRAILING_RE = re.compile(
    r"\s*(Profile|Resume|CV|Curriculum Vitae|Bio|Portfolio)$", re.I
)


def _extract_name(non_blank_lines: list[str]) -> str:
    """Heuristic: first non-blank line that isn't an email/URL/phone and is
    short enough to be a person's name."""
    for line in non_blank_lines[:5]:
        stripped = line.strip()
        if not stripped:
            continue
        if "@" in stripped or "http" in stripped.lower():
            continue
        if _PHONE_RE.search(stripped) and len(stripped) < 20:
            continue
        # Reasonable name: 2-60 chars, no digit runs longer than 4
        if 2 <= len(stripped) <= 60 and not re.search(r"\d{5,}", stripped):
            return _NAME_TRAILING_RE.sub("", stripped).strip()
    return ""


def _extract_email(text: str) -> str:
    m = _EMAIL_RE.search(text)
    return m.group(0).lower() if m else ""


def _extract_phone(text: str) -> str:
    m = _PHONE_RE.search(text)
    if m:
        raw = m.group(0).strip()
        # Must be at least 7 digits total
        if len(re.sub(r"\D", "", raw)) >= 7:
            return raw
    return ""


def _extract_location(text: str) -> str:
    m = _LOCATION_RE.search(text)
    return m.group(0).strip() if m else ""


def _extract_section_headers(lines: list[str]) -> list[str]:
    headers = []
    for line in lines:
        stripped = line.strip()
        if _SECTION_HEADER_RE.match(stripped):
            canonical = stripped.rstrip(":").strip().upper()
            if canonical in _KNOWN_HEADERS or len(canonical) <= 30:
                headers.append(canonical)
    return list(dict.fromkeys(headers))  # deduplicate, preserve order


# ---------------------------------------------------------------------------
# Job-description heuristics
# ---------------------------------------------------------------------------

_YEARS_RE = re.compile(
    r"(\d+)\+?\s*(?:–|-|to|or more)?\s*(?:\d+\s*)?years?",
    re.I,
)

_SUBJECT_RE = re.compile(r"Subject:\s*(.+)", re.I)


def extract_job_heuristics(text: str) -> dict[str, Any]:
    """Return heuristically extracted job description fields."""
    return {
        "min_experience_years": _extract_min_years(text),
        "location": _extract_location(text),
        "title_hint": _extract_title_hint(text),
        "_source": "heuristic",
    }


def _extract_min_years(text: str) -> int:
    """Take the first explicit year count found, rounded down."""
    for m in _YEARS_RE.finditer(text):
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return 0


def _extract_title_hint(text: str) -> str:
    """Try to pull a role title from an email Subject line."""
    m = _SUBJECT_RE.search(text)
    if m:
        subject = m.group(1).strip()
        # Strip common prefixes like "Urgent - " or "Re: "
        subject = re.sub(r"^(Re:|Fwd:|Urgent\s*[-–]?\s*)", "", subject, flags=re.I).strip()
        return subject
    return ""
