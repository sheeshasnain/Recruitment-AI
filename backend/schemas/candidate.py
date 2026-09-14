from pydantic import BaseModel, EmailStr, Field


class CandidateInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    phone: str | None = None
    resume_text: str = Field(..., min_length=20)


class CandidateProfile(BaseModel):
    name: str
    email: str
    phone: str | None = None

    current_role: str | None = None
    years_experience: float = 0

    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience_summary: str = ""

    strengths: list[str] = Field(default_factory=list)