from pydantic import BaseModel, Field


class JobInput(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: str = Field(..., min_length=10)
    required_skills: list[str] = Field(default_factory=list)
    minimum_experience: float = Field(default=0, ge=0)