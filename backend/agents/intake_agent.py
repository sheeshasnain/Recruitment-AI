from backend.agents.state import RecruitmentState
from backend.schemas.candidate import CandidateProfile
from backend.services.llm_service import get_llm


async def candidate_intake_agent(
    state: RecruitmentState,
) -> dict:
    llm = get_llm(temperature=0)

    structured_llm = llm.with_structured_output(
        CandidateProfile
    )

    prompt = f"""
You are a recruitment candidate intake specialist.

Analyze the candidate resume below.

Extract only information supported by the resume.

Do not invent skills, education, roles, or experience.

Candidate name:
{state["candidate_name"]}

Candidate email:
{state["candidate_email"]}

Candidate phone:
{state.get("candidate_phone") or "Not provided"}

Resume:
----------------
{state["resume_text"]}
----------------

Return a structured candidate profile.
"""

    profile = await structured_llm.ainvoke(prompt)

    # Preserve recruiter-provided identity fields.
    profile.name = state["candidate_name"]
    profile.email = state["candidate_email"]
    profile.phone = state.get("candidate_phone")

    return {
        "candidate_profile": profile
    }