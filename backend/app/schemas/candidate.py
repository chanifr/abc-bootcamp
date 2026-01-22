"""Candidate schemas matching Exercise 1 JSON contract."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.candidate import CandidateStatus
from app.models.document import DocumentType
from app.models.skill import SkillLevel


# Nested schemas
class ExperienceSchema(BaseModel):
    """Work experience schema."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    company: str
    title: str
    start_date: date = Field(alias="startDate")
    end_date: Optional[date] = Field(alias="endDate")
    description: str


class EducationSchema(BaseModel):
    """Education schema."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    institution: str
    degree: str
    field: str
    start_date: date = Field(alias="startDate")
    end_date: Optional[date] = Field(alias="endDate")


class SkillSchema(BaseModel):
    """Skill schema."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    level: SkillLevel


class DocumentSchema(BaseModel):
    """Document schema."""

    model_config = ConfigDict(from_attributes=True)

    type: DocumentType
    name: str
    url: str


# Main candidate schemas
class CandidateListItem(BaseModel):
    """Candidate list item (summary view)."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    email: EmailStr
    phone: str
    location: str
    summary: str
    status: CandidateStatus
    years_of_experience: int = Field(alias="yearsOfExperience")
    sort_order: int = Field(alias="sortOrder")

    # Preview data
    skills: list[SkillSchema] = []
    applied_positions: list[str] = Field(default=[], alias="appliedPositions")


class CandidateDetail(BaseModel):
    """Candidate detail (full view)."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    email: EmailStr
    phone: str
    location: str
    summary: str
    status: CandidateStatus
    years_of_experience: int = Field(alias="yearsOfExperience")
    sort_order: int = Field(alias="sortOrder")

    # Full nested data
    experience: list[ExperienceSchema] = []
    education: list[EducationSchema] = []
    skills: list[SkillSchema] = []
    documents: list[DocumentSchema] = []
    applied_positions: list[str] = Field(default=[], alias="appliedPositions")


class CandidateListResponse(BaseModel):
    """Response for candidate list endpoint."""

    candidates: list[CandidateListItem]
    total: int
