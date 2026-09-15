from backend.schemas.evaluation import (
    InterviewSemanticEvaluation,
)
from backend.services.interview_scoring_service import (
    calculate_interview_score,
)


def test_interview_scoring():

    evaluation = (
        InterviewSemanticEvaluation(
            technical=80,
            problem_solving=80,
            experience=80,
            communication=80,
            strengths=[],
            concerns=[],
            summary="Test",
        )
    )

    score, recommendation = (
        calculate_interview_score(
            evaluation
        )
    )

    assert score == 80

    assert (
        recommendation
        == "strong_recommendation"
    )


def test_low_interview_score():

    evaluation = (
        InterviewSemanticEvaluation(
            technical=40,
            problem_solving=40,
            experience=40,
            communication=40,
            strengths=[],
            concerns=[],
            summary="Test",
        )
    )

    score, recommendation = (
        calculate_interview_score(
            evaluation
        )
    )

    assert score == 40

    assert (
        recommendation
        == "not_recommended"
    )