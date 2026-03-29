"""CV extraction prompt — version 1.

Changing this file changes prompt_version stored in extraction_artifacts,
making it easy to compare outputs across prompt versions.
"""

VERSION = "cv_v1"

SYSTEM = """\
You are a structured data extraction engine.
Your only job is to read a CV/resume and return a JSON object with the fields described.
Return ONLY valid JSON — no markdown fences, no explanation, no extra text.
If a field cannot be confidently determined, use null or an empty list.
Do not invent information that is not in the document.
"""

USER_TEMPLATE = """\
Extract structured information from the following CV text.

Return a JSON object with exactly these keys:

{{
  "candidate_summary": "<3-5 sentence human-readable summary of who this person is, \
their main skills, and their career level. Suitable for a recruiter to read. \
Must be based only on the CV content.>",
  "skills": [
    {{"name": "<skill name>", "level": "<Beginner|Intermediate|Advanced|Expert>"}}
  ],
  "experiences": [
    {{
      "company": "<company name>",
      "title": "<job title>",
      "start_date": "<YYYY-MM or null>",
      "end_date": "<YYYY-MM or null — null means current role>",
      "description": "<1-2 sentence summary of responsibilities>"
    }}
  ],
  "education": [
    {{
      "institution": "<school/university name>",
      "degree": "<degree type, e.g. Bachelor of Science>",
      "field": "<field of study>",
      "start_date": "<YYYY-MM or null>",
      "end_date": "<YYYY-MM or null>"
    }}
  ]
}}

Rules:
- skill.level must be one of: Beginner, Intermediate, Advanced, Expert
- Infer skill level from context (years mentioned, seniority, certifications)
- If level cannot be inferred, use "Intermediate"
- Include only real skills explicitly mentioned or strongly implied by the CV
- candidate_summary must be non-empty
- Keep descriptions factual; do not embellish

CV TEXT:
---
{raw_text}
---
"""


def build_prompt(raw_text: str) -> tuple[str, str, str]:
    """Return (system_prompt, user_prompt, version)."""
    return SYSTEM, USER_TEMPLATE.format(raw_text=raw_text), VERSION
