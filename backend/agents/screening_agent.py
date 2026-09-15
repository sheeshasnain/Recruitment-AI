from backend.agents.state import RecruitmentState
from backend.schemas.screening import (
    LLMScreeningAssessment,
)
from backend.services.llm_service import get_llm
from backend.services.scoring_service import (
    calculate_screening_result,
)


async def screening_agent(
    state: RecruitmentState,
) -> dict:

    llm = get_llm(
        temperature=0
    )

    structured_llm = (
        llm.with_structured_output(
            LLMScreeningAssessment
        )
    )

    candidate = state[
        "candidate_profile"
    ]

    job = state["job"]

    prompt = f"""
You are a recruitment screening assistant.

Evaluate the candidate only against the stated
job-related requirements.

Do NOT assign numerical scores.

Do NOT make a final hiring decision.

Your task is only to identify:

- matched required skills
- missing required skills
- relevant strengths
- job-related concerns
- concise reasoning

Do not use or infer protected characteristics.

Do not invent candidate experience or skills.

JOB

Title:
{job.title}

Description:
{job.description}

Required skills:
{", ".join(job.required_skills)}

Minimum experience:
{job.minimum_experience} years


CANDIDATE

Current role:
{candidate.current_role}

Years experience:
{candidate.years_experience}

Skills:
{", ".join(candidate.skills)}

Experience summary:
{candidate.experience_summary}


Return only the requested structured assessment.
"""

    assessment = await structured_llm.ainvoke(
        prompt
    )

    result = calculate_screening_result(
        candidate=candidate,
        job=job,
        assessment=assessment,
    )

    return {
        "screening_result": result
    }


def determine_screening_route(
    state: RecruitmentState,
) -> dict:

    result = state[
        "screening_result"
    ]

    return {
        "route": result.recommendation
    }