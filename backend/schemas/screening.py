from typing import Literal

from pydantic import BaseModel, Field

from backend.schemas.candidate import CandidateInput
from backend.schemas.job import JobInput


class LLMScreeningAssessment(BaseModel):

    matched_skills: list[str] = Field(
        default_factory=list
    )

    missing_skills: list[str] = Field(
        default_factory=list
    )

    strengths: list[str] = Field(
        default_factory=list
    )

    concerns: list[str] = Field(
        default_factory=list
    )

    reasoning: str


class ScreeningResult(BaseModel):

    skills_score: float = Field(
        ge=0,
        le=100,
    )

    experience_score: float = Field(
        ge=0,
        le=100,
    )

    matched_skills: list[str] = Field(
        default_factory=list
    )

    missing_skills: list[str] = Field(
        default_factory=list
    )

    strengths: list[str] = Field(
        default_factory=list
    )

    concerns: list[str] = Field(
        default_factory=list
    )

    overall_score: float = Field(
        ge=0,
        le=100,
    )

    recommendation: Literal[
        "shortlist",
        "manual_review",
        "reject",
    ]

    reasoning: str


class ScreeningRequest(BaseModel):

    candidate: CandidateInput

    job: JobInput


class ScreeningResponse(BaseModel):

    candidate_profile: dict

    screening_result: dict

    route: str