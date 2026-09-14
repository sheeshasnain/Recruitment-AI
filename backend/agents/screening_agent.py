from backend.agents.state import RecruitmentState
from backend.schemas.screening import ScreeningResult
from backend.services.llm_service import get_llm


async def screening_agent(
    state: RecruitmentState,
) -> dict:
    llm = get_llm(temperature=0)

    structured_llm = llm.with_structured_output(
        ScreeningResult
    )

    candidate = state["candidate_profile"]
    job = state["job"]

    prompt = f"""
You are a recruitment screening assistant.

Evaluate the candidate against the job requirements.

Do not make assumptions about protected or personal characteristics.
Evaluate only job-relevant information such as skills,
experience and role relevance.

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


Return a structured screening assessment.

Scoring:
0-100 for each score.

Recommendation guidance:

shortlist:
strong job-related match

manual_review:
mixed or uncertain match

reject:
clear mismatch with the stated job requirements

Do not reject based on missing information alone.
Use manual_review when evidence is insufficient.
"""

    result = await structured_llm.ainvoke(prompt)

    return {
        "screening_result": result
    }

def determine_screening_route(
    state: RecruitmentState,
) -> dict:
    result = state["screening_result"]

    score = result.overall_score

    if score >= 75:
        route = "shortlist"

    elif score >= 50:
        route = "manual_review"

    else:
        route = "reject"

    return {
        "route": route
    }