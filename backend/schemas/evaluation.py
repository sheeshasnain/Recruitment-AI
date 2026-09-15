from typing import Literal

from pydantic import BaseModel, Field


class AnswerEvaluation(BaseModel):

    relevance: float = Field(
        ge=0,
        le=100,
    )

    depth: float = Field(
        ge=0,
        le=100,
    )

    clarity: float = Field(
        ge=0,
        le=100,
    )

    evidence: float = Field(
        ge=0,
        le=100,
    )

    strengths: list[str] | None = Field(
        default_factory=list
    )

    concerns: list[str] | None = Field(
        default_factory=list
    )

    reasoning: str


class InterviewSemanticEvaluation(BaseModel):

    technical: float = Field(
        ge=0,
        le=100,
    )

    communication: float = Field(
        ge=0,
        le=100,
    )

    problem_solving: float = Field(
        ge=0,
        le=100,
    )

    experience: float = Field(
        ge=0,
        le=100,
    )

    strengths: list[str] | None = Field(
        default_factory=list
    )

    concerns: list[str] | None = Field(
        default_factory=list
    )

    summary: str