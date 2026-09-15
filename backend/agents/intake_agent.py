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

Analyze the resume and extract structured candidate information.

STRICT RULES:

1. Extract only information supported by the resume.
2. Never invent employment, education, skills, experience,
   job titles, or achievements.
3. All fields that are arrays MUST ALWAYS be JSON arrays.
4. Never return null for an array field.
5. If an array has no supported values, return [].
6. If the current role cannot be determined, return null.
7. If years of professional experience cannot be determined,
   return 0.
8. strengths MUST always be an array of strings.
9. skills MUST always be an array of strings.
10. education MUST always be an array of strings.

Examples:

No strengths:
"strengths": []

No skills:
"skills": []

No education:
"education": []

Unknown current role:
"current_role": null


Candidate name:
{state["candidate_name"]}

Candidate email:
{state["candidate_email"]}

Candidate phone:
{state.get("candidate_phone") or "Not provided"}


RESUME
--------------------------------

{state["resume_text"]}

--------------------------------

Return the candidate profile using the required structured format.

IMPORTANT:
Never return null for skills, education, or strengths.
Use [] when no values can be extracted.
"""

    profile = await structured_llm.ainvoke(
        prompt
    )
    
    profile.skills = profile.skills or []
    profile.education = profile.education or []
    profile.strengths = profile.strengths or []
    profile.experience_summary = (
    profile.experience_summary or ""
    )



    # Identity comes from recruiter input rather than
    # relying on the LLM to extract it.
    profile.name = state["candidate_name"]
    profile.email = state["candidate_email"]
    profile.phone = state.get(
        "candidate_phone"
    )

    return {
        "candidate_profile": profile
    }