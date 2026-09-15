from backend.schemas.evaluation import (
    InterviewSemanticEvaluation,
)


TECHNICAL_WEIGHT = 0.40
PROBLEM_SOLVING_WEIGHT = 0.25
EXPERIENCE_WEIGHT = 0.20
COMMUNICATION_WEIGHT = 0.15


def calculate_interview_score(
    evaluation: InterviewSemanticEvaluation,
) -> tuple[float, str]:

    score = (
        evaluation.technical
        * TECHNICAL_WEIGHT
        +
        evaluation.problem_solving
        * PROBLEM_SOLVING_WEIGHT
        +
        evaluation.experience
        * EXPERIENCE_WEIGHT
        +
        evaluation.communication
        * COMMUNICATION_WEIGHT
    )

    score = round(
        score,
        2,
    )

    if score >= 80:

        recommendation = (
            "strong_recommendation"
        )

    elif score >= 65:

        recommendation = (
            "recommend"
        )

    elif score >= 50:

        recommendation = (
            "manual_review"
        )

    else:

        recommendation = (
            "not_recommended"
        )

    return (
        score,
        recommendation,
    )