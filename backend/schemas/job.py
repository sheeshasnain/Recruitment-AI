from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobInput(BaseModel):

    title: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

    description: str = Field(
        ...,
        min_length=10,
    )

    required_skills: list[str] = Field(
        default_factory=list
    )

    minimum_experience: float = Field(
        default=0,
        ge=0,
    )


class JobCreate(JobInput):
    pass


class JobRead(JobInput):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    is_active: bool
    created_at: datetime