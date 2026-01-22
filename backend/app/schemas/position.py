"""Position schemas matching Exercise 1 JSON contract."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.position import PositionStatus


class PositionListItem(BaseModel):
    """Position list item (summary view)."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    title: str
    department: str
    location: str
    description: str
    requirements: str
    required_skills: list[str] = Field(default=[], alias="requiredSkills")
    min_experience_years: int = Field(alias="minExperienceYears")
    status: PositionStatus
    posted_date: date = Field(alias="postedDate")
    candidates: list[str] = []  # Array of candidate IDs
    sort_order: int = Field(alias="sortOrder")


class PositionDetail(BaseModel):
    """Position detail (full view) - same as list item for now."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    title: str
    department: str
    location: str
    description: str
    requirements: str
    required_skills: list[str] = Field(default=[], alias="requiredSkills")
    min_experience_years: int = Field(alias="minExperienceYears")
    status: PositionStatus
    posted_date: date = Field(alias="postedDate")
    candidates: list[str] = []  # Array of candidate IDs
    sort_order: int = Field(alias="sortOrder")


class PositionUpdate(BaseModel):
    """Position update schema."""

    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1)
    department: str = Field(min_length=1)
    location: str = Field(min_length=1)
    description: str = Field(min_length=1)
    requirements: str = Field(min_length=1)
    required_skills: list[str] = Field(alias="requiredSkills")
    min_experience_years: int = Field(ge=0, alias="minExperienceYears")
    status: PositionStatus
    posted_date: date = Field(alias="postedDate")

    @field_validator("required_skills")
    @classmethod
    def validate_skills_not_empty(cls, v):
        """Ensure skills list is provided (can be empty array)."""
        if v is None:
            raise ValueError("requiredSkills must be provided")
        return v


class PositionListResponse(BaseModel):
    """Response for position list endpoint."""

    positions: list[PositionListItem]
    total: int
