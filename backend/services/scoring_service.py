from backend.schemas.candidate import CandidateProfile
from backend.schemas.job import JobInput
from backend.schemas.screening import (
    LLMScreeningAssessment,
    ScreeningResult,
)


SKILLS_WEIGHT = 0.65
EXPERIENCE_WEIGHT = 0.35


def normalize_skill(
    value: str,
) -> str:

    return " ".join(
        value.casefold().strip().split()
    )


def calculate_screening_result(
    candidate: CandidateProfile,
    job: JobInput,
    assessment: LLMScreeningAssessment,
) -> ScreeningResult:

    required_skills = {
        normalize_skill(skill)
        for skill in job.required_skills
    }

    llm_matched = {
        normalize_skill(skill)
        for skill in assessment.matched_skills
    }

    # Only skills that genuinely appear in the
    # required-skills list can count toward score.
    valid_matches = (
        required_skills
        & llm_matched
    )

    if required_skills:
        skills_score = (
            len(valid_matches)
            / len(required_skills)
        ) * 100

    else:
        skills_score = 100


    minimum_experience = (
        job.minimum_experience
    )

    if minimum_experience <= 0:
        experience_score = 100

    else:
        experience_ratio = (
            candidate.years_experience
            / minimum_experience
        )

        experience_score = min(
            experience_ratio * 100,
            100,
        )


    overall_score = (
        skills_score * SKILLS_WEIGHT
        + experience_score
        * EXPERIENCE_WEIGHT
    )

    overall_score = round(
        overall_score,
        2,
    )

    skills_score = round(
        skills_score,
        2,
    )

    experience_score = round(
        experience_score,
        2,
    )


    if overall_score >= 75:
        recommendation = "shortlist"

    elif overall_score >= 50:
        recommendation = "manual_review"

    else:
        recommendation = "reject"


    return ScreeningResult(

        skills_score=skills_score,

        experience_score=experience_score,

        matched_skills=(
            assessment.matched_skills
        ),

        missing_skills=(
            assessment.missing_skills
        ),

        strengths=(
            assessment.strengths
        ),

        concerns=(
            assessment.concerns
        ),

        overall_score=overall_score,

        recommendation=recommendation,

        reasoning=assessment.reasoning,
    )