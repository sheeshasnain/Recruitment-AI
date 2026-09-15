from typing import Literal

from pydantic import BaseModel, Field


class RecruiterDecisionRequest(BaseModel):

    decision: Literal[
        "approve",
        "hold",
        "reject",
    ]

    notes: str | None = Field(
        default=None,
        max_length=3000,
    )
    

class GeneratedInterviewQuestion(BaseModel):

    question: str

    category: Literal[
        "technical",
        "experience",
        "problem_solving",
        "behavioral",
        "role_specific",
    ]

    difficulty: Literal[
        "easy",
        "medium",
        "hard",
    ]

    expected_points: list[str] = Field(
        default_factory=list
    )

    weight: float = Field(
        default=1.0,
        ge=0.1,
        le=5.0,
    )


class InterviewQuestionSet(BaseModel):

    questions: list[
        GeneratedInterviewQuestion
    ]


class PrepareInterviewRequest(BaseModel):

    number_of_questions: int = Field(
        default=8,
        ge=5,
        le=15,
    )


class AnswerSubmitRequest(BaseModel):

    answer: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )


class FollowUpRequest(BaseModel):

    question_id: int


class FollowUpQuestion(BaseModel):

    question: str

    reason: str


class CompleteInterviewRequest(BaseModel):

    recruiter_notes: str | None = Field(
        default=None,
        max_length=5000,
    )