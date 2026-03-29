"""Unit tests for the heuristic extractor.

These tests are fast, fully deterministic, and require no DB or LLM.
"""
import pytest

from app.services.ingestion.heuristic_extractor import (
    extract_cv_heuristics,
    extract_job_heuristics,
)


# ---------------------------------------------------------------------------
# CV heuristic tests
# ---------------------------------------------------------------------------

SAMPLE_CV = """
John Smith
john.smith@example.com
+1 (555) 123-4567
New York, NY

EXPERIENCE
Senior Engineer at Acme Corp, 2020 - present
Led backend development.

EDUCATION
MIT — B.S. Computer Science, 2016

SKILLS
Python, AWS, Docker
"""


def test_cv_extracts_email():
    result = extract_cv_heuristics(SAMPLE_CV)
    assert result["email"] == "john.smith@example.com"


def test_cv_extracts_phone():
    result = extract_cv_heuristics(SAMPLE_CV)
    assert result["phone"] != ""
    assert "555" in result["phone"]


def test_cv_extracts_location():
    result = extract_cv_heuristics(SAMPLE_CV)
    assert "New York" in result["location"]


def test_cv_extracts_name():
    result = extract_cv_heuristics(SAMPLE_CV)
    assert result["name"] == "John Smith"


def test_cv_extracts_section_headers():
    result = extract_cv_heuristics(SAMPLE_CV)
    assert "EXPERIENCE" in result["section_headers"]
    assert "EDUCATION" in result["section_headers"]
    assert "SKILLS" in result["section_headers"]


def test_cv_missing_email_returns_empty():
    result = extract_cv_heuristics("John Doe\n+1 555 999 0000\nNew York, NY")
    assert result["email"] == ""


def test_cv_missing_phone_returns_empty():
    result = extract_cv_heuristics("John Doe\njohn@example.com\nNew York, NY")
    assert result["phone"] == ""


def test_cv_source_is_heuristic():
    result = extract_cv_heuristics(SAMPLE_CV)
    assert result["_source"] == "heuristic"


def test_cv_email_is_lowercased():
    result = extract_cv_heuristics("Jane Doe\nJANE.DOE@COMPANY.COM\n")
    assert result["email"] == "jane.doe@company.com"


def test_cv_no_false_phone_from_year():
    # A year alone should not match as a phone number
    result = extract_cv_heuristics("Alice\nalice@x.com\nExperience: 2019 - 2022\n")
    # phone may be empty or a match but must not be just "2019"
    if result["phone"]:
        assert len(result["phone"].replace(" ", "").replace("-", "")) >= 7


# ---------------------------------------------------------------------------
# Job description heuristic tests
# ---------------------------------------------------------------------------

SAMPLE_JD = """
From: HR <hr@company.com>
Subject: Urgent - Senior DevOps Engineer Needed

We need 5+ years of hands-on DevOps experience.
The role is based in Tel Aviv, IL.
"""


def test_job_extracts_min_years():
    result = extract_job_heuristics(SAMPLE_JD)
    assert result["min_experience_years"] == 5


def test_job_extracts_location():
    result = extract_job_heuristics(SAMPLE_JD)
    assert "Tel Aviv" in result["location"]


def test_job_extracts_title_hint_from_subject():
    result = extract_job_heuristics(SAMPLE_JD)
    assert "DevOps" in result["title_hint"]


def test_job_zero_years_when_not_mentioned():
    result = extract_job_heuristics("We are hiring a cloud engineer.")
    assert result["min_experience_years"] == 0


def test_job_source_is_heuristic():
    result = extract_job_heuristics(SAMPLE_JD)
    assert result["_source"] == "heuristic"
