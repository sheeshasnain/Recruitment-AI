from typing import TypedDict

from backend.schemas.interview import (
    InterviewQuestionSet,
)


class InterviewState(
    TypedDict,
    total=False,
):

    application_id: int

    job_title: str
    job_description: str
    required_skills: list[str]

    candidate_skills: list[str]
    candidate_summary: str

    screening_strengths: list[str]
    screening_concerns: list[str]

    number_of_questions: int

    generated_questions: (
        InterviewQuestionSet
    )

    status: str