"""Job description extraction prompt — version 1."""

VERSION = "job_v1"

SYSTEM = """\
You are a structured data extraction engine.
Your only job is to read a job description (which may be written as an email or prose) \
and return a JSON object with the fields described.
Return ONLY valid JSON — no markdown fences, no explanation, no extra text.
If a field cannot be confidently determined, use null or an empty list.
Do not invent information that is not in the document.
"""

USER_TEMPLATE = """\
Extract structured information from the following job description text.

Return a JSON object with exactly these keys:

{{
  "title": "<exact job title being filled>",
  "department": "<department or team, e.g. Engineering, Infrastructure, Product>",
  "location": "<work location; use Remote if fully remote>",
  "description": "<2-4 sentence description of the role and its main responsibilities>",
  "requirements": "<2-4 sentence summary of required qualifications and experience>",
  "min_experience_years": <integer — minimum years of relevant experience required, or 0>,
  "required_skills": ["<skill name>"],
  "position_summary": "<2-3 sentence human-readable summary for a recruiter. \
Include role level, key technologies, and what makes this role distinct.>"
}}

Rules:
- title must be non-empty
- required_skills should list concrete technologies, tools, or practices
- min_experience_years must be an integer (0 if not specified)
- All string fields must be non-empty where information is available

JOB DESCRIPTION TEXT:
---
{raw_text}
---
"""


def build_prompt(raw_text: str) -> tuple[str, str, str]:
    """Return (system_prompt, user_prompt, version)."""
    return SYSTEM, USER_TEMPLATE.format(raw_text=raw_text), VERSION
