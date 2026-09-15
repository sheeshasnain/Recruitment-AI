from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CandidateInput(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    phone: str | None = None

    resume_text: str = Field(
        ...,
        min_length=20,
    )


class CandidateProfile(BaseModel):
    name: str
    email: str
    phone: str | None = None

    current_role: str | None = None
    years_experience: float = 0

    skills: list[str] | None = Field(
        default_factory=list
    )

    education: list[str] | None = Field(
        default_factory=list
    )

    experience_summary: str = ""

    strengths: list[str] | None = Field(
        default_factory=list
    )

class CandidateRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    name: str
    email: str
    phone: str | None

    resume_filename: str | None

    current_role: str | None
    years_experience: float

    skills: list
    education: list

    experience_summary: str | None

    created_at: datetime