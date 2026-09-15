from backend.schemas.candidate import (
    CandidateProfile,
)
from backend.schemas.job import JobInput
from backend.schemas.screening import (
    LLMScreeningAssessment,
)
from backend.services.scoring_service import (
    calculate_screening_result,
)


def test_perfect_candidate_score():

    candidate = CandidateProfile(
        name="Test Candidate",
        email="test@example.com",
        current_role="UI/UX Designer",
        years_experience=5,
        skills=[
            "Figma",
            "User Research",
            "Prototyping",
        ],
        education=[],
        experience_summary=(
            "Five years of design experience."
        ),
        strengths=[],
    )


    job = JobInput(
        title="UI/UX Designer",
        description=(
            "Experienced UI UX designer required."
        ),
        required_skills=[
            "Figma",
            "User Research",
            "Prototyping",
        ],
        minimum_experience=4,
    )


    assessment = LLMScreeningAssessment(
        matched_skills=[
            "Figma",
            "User Research",
            "Prototyping",
        ],
        missing_skills=[],
        strengths=[],
        concerns=[],
        reasoning="Strong match.",
    )


    result = calculate_screening_result(
        candidate=candidate,
        job=job,
        assessment=assessment,
    )


    assert result.skills_score == 100
    assert result.experience_score == 100
    assert result.overall_score == 100
    assert result.recommendation == "shortlist"