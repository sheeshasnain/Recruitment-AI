from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApplicationScreenRequest(
    BaseModel
):
    candidate_id: int
    job_id: int


class ApplicationRead(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    candidate_id: int
    job_id: int

    status: str
    screening_route: str | None

    matched_skills: list
    missing_skills: list

    strengths: list
    concerns: list

    skills_score: float | None

    experience_score: float | None

    overall_score: float | None

    reasoning: str | None

    created_at: datetime