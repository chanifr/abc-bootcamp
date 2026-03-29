"""Unit tests for the LLM output validator.

Tests both success paths and failure modes.
Validation must fail loudly — no silent defaults for bad data.
"""
import pytest

from app.services.ingestion.validator import (
    ValidationError,
    validate_cv_extraction,
    validate_job_extraction,
)


# ---------------------------------------------------------------------------
# CV validation — success cases
# ---------------------------------------------------------------------------

VALID_CV_DATA = {
    "candidate_summary": "Experienced engineer with 5 years in cloud infrastructure.",
    "skills": [
        {"name": "Python", "level": "Advanced"},
        {"name": "AWS", "level": "Expert"},
    ],
    "experiences": [
        {
            "company": "Acme",
            "title": "Senior Engineer",
            "start_date": "2020-01",
            "end_date": None,
            "description": "Led cloud platform team.",
        }
    ],
    "education": [
        {
            "institution": "MIT",
            "degree": "B.S.",
            "field": "Computer Science",
            "start_date": "2015-09",
            "end_date": "2019-05",
        }
    ],
}


def test_cv_valid_data_passes():
    result = validate_cv_extraction(VALID_CV_DATA)
    assert result["candidate_summary"] == VALID_CV_DATA["candidate_summary"]
    assert len(result["skills"]) == 2
    assert result["skills"][0]["name"] == "Python"
    assert result["skills"][0]["level"] == "Advanced"


def test_cv_skill_levels_normalised():
    data = {**VALID_CV_DATA, "skills": [{"name": "Terraform", "level": "senior"}]}
    result = validate_cv_extraction(data)
    assert result["skills"][0]["level"] == "Advanced"


def test_cv_unknown_level_defaults_to_intermediate():
    data = {**VALID_CV_DATA, "skills": [{"name": "Rust", "level": "guru"}]}
    result = validate_cv_extraction(data)
    assert result["skills"][0]["level"] == "Intermediate"


def test_cv_skill_without_level_defaults_to_intermediate():
    data = {**VALID_CV_DATA, "skills": [{"name": "Go"}]}
    result = validate_cv_extraction(data)
    assert result["skills"][0]["level"] == "Intermediate"


def test_cv_empty_skills_allowed():
    data = {**VALID_CV_DATA, "skills": []}
    result = validate_cv_extraction(data)
    assert result["skills"] == []


def test_cv_skills_with_nameless_entry_skipped():
    data = {**VALID_CV_DATA, "skills": [{"name": "", "level": "Expert"}, {"name": "Go", "level": "Beginner"}]}
    result = validate_cv_extraction(data)
    assert len(result["skills"]) == 1
    assert result["skills"][0]["name"] == "Go"


def test_cv_non_object_skill_skipped():
    data = {**VALID_CV_DATA, "skills": ["Python", {"name": "Rust", "level": "Advanced"}]}
    result = validate_cv_extraction(data)
    assert len(result["skills"]) == 1
    assert result["skills"][0]["name"] == "Rust"


def test_cv_experiences_returned():
    result = validate_cv_extraction(VALID_CV_DATA)
    assert len(result["experiences"]) == 1
    assert result["experiences"][0]["company"] == "Acme"


def test_cv_education_returned():
    result = validate_cv_extraction(VALID_CV_DATA)
    assert len(result["education"]) == 1
    assert result["education"][0]["institution"] == "MIT"


# ---------------------------------------------------------------------------
# CV validation — failure cases
# ---------------------------------------------------------------------------

def test_cv_missing_summary_raises():
    data = {**VALID_CV_DATA, "candidate_summary": ""}
    with pytest.raises(ValidationError, match="candidate_summary"):
        validate_cv_extraction(data)


def test_cv_none_summary_raises():
    data = {**VALID_CV_DATA, "candidate_summary": None}
    with pytest.raises(ValidationError, match="candidate_summary"):
        validate_cv_extraction(data)


def test_cv_summary_too_long_raises():
    data = {**VALID_CV_DATA, "candidate_summary": "x" * 3001}
    with pytest.raises(ValidationError, match="too long"):
        validate_cv_extraction(data)


def test_cv_non_dict_raises():
    with pytest.raises(ValidationError):
        validate_cv_extraction(["not", "a", "dict"])


def test_cv_skills_non_list_raises():
    data = {**VALID_CV_DATA, "skills": "Python, AWS"}
    with pytest.raises(ValidationError, match="skills must be a list"):
        validate_cv_extraction(data)


# ---------------------------------------------------------------------------
# Job validation — success cases
# ---------------------------------------------------------------------------

VALID_JOB_DATA = {
    "title": "Senior DevOps Engineer",
    "department": "Infrastructure",
    "location": "Tel Aviv, IL",
    "description": "Lead infrastructure automation initiatives.",
    "requirements": "5+ years DevOps, Kubernetes, Terraform.",
    "min_experience_years": 5,
    "required_skills": ["AWS", "Kubernetes", "Terraform"],
    "position_summary": "Senior role in a fast-paced fintech.",
}


def test_job_valid_data_passes():
    result = validate_job_extraction(VALID_JOB_DATA)
    assert result["title"] == "Senior DevOps Engineer"
    assert result["min_experience_years"] == 5
    assert "AWS" in result["required_skills"]


def test_job_min_years_coerced_to_int():
    data = {**VALID_JOB_DATA, "min_experience_years": "3"}
    result = validate_job_extraction(data)
    assert result["min_experience_years"] == 3


def test_job_min_years_negative_clamped_to_zero():
    data = {**VALID_JOB_DATA, "min_experience_years": -1}
    result = validate_job_extraction(data)
    assert result["min_experience_years"] == 0


def test_job_min_years_null_defaults_to_zero():
    data = {**VALID_JOB_DATA, "min_experience_years": None}
    result = validate_job_extraction(data)
    assert result["min_experience_years"] == 0


def test_job_skills_empty_list_allowed():
    data = {**VALID_JOB_DATA, "required_skills": []}
    result = validate_job_extraction(data)
    assert result["required_skills"] == []


def test_job_department_defaults_when_missing():
    data = {k: v for k, v in VALID_JOB_DATA.items() if k != "department"}
    result = validate_job_extraction(data)
    assert result["department"] == "Engineering"


# ---------------------------------------------------------------------------
# Job validation — failure cases
# ---------------------------------------------------------------------------

def test_job_missing_title_raises():
    data = {**VALID_JOB_DATA, "title": ""}
    with pytest.raises(ValidationError, match="title"):
        validate_job_extraction(data)


def test_job_missing_description_raises():
    data = {**VALID_JOB_DATA, "description": ""}
    with pytest.raises(ValidationError, match="description"):
        validate_job_extraction(data)


def test_job_non_dict_raises():
    with pytest.raises(ValidationError):
        validate_job_extraction("just a string")
