import json

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

All list fields must be arrays.
Never return null for list fields.
"""

    # --------------------------------------------------
    # FIRST ATTEMPT:
    # Use Groq/LangChain structured output
    # --------------------------------------------------

    try:

        structured_llm = (
            llm.with_structured_output(
                LLMScreeningAssessment
            )
        )

        assessment = (
            await structured_llm.ainvoke(
                prompt
            )
        )

    except Exception as structured_error:

        # --------------------------------------------------
        # FALLBACK:
        # Some Groq models generate the correct JSON but
        # fail to perform the structured-output tool call.
        # In that case, request normal JSON instead.
        # --------------------------------------------------

        print(
            "Structured screening output failed."
        )

        print(
            "Using JSON fallback."
        )

        print(
            f"Error: {structured_error}"
        )

        fallback_prompt = f"""
{prompt}

The structured-output mechanism was unavailable.

Return ONLY valid JSON.

Do not use markdown.
Do not use code fences.
Do not include text before or after the JSON.

Use exactly these fields:

{{
    "matched_skills": [],
    "missing_skills": [],
    "strengths": [],
    "concerns": [],
    "reasoning": ""
}}

Rules:

- matched_skills must be an array of strings
- missing_skills must be an array of strings
- strengths must be an array of strings
- concerns must be an array of strings
- reasoning must be a string
- never return null for an array
"""

        response = await llm.ainvoke(
            fallback_prompt
        )

        content = response.content

        # Some providers can return content
        # in a list-like structure.
        if isinstance(content, list):
            content = "".join(
                str(item)
                for item in content
            )

        content = str(content).strip()

        # Remove accidental Markdown fences.
        if content.startswith("```json"):
            content = content[
                len("```json"):
            ].strip()

        elif content.startswith("```"):
            content = content[
                len("```"):
            ].strip()

        if content.endswith("```"):
            content = content[:-3].strip()

        # Find the JSON object in case the model
        # accidentally includes surrounding text.
        json_start = content.find("{")
        json_end = content.rfind("}")

        if (
            json_start == -1
            or json_end == -1
        ):
            raise ValueError(
                "Groq fallback did not "
                "return a JSON object."
            )

        json_text = content[
            json_start:json_end + 1
        ]

        data = json.loads(
            json_text
        )

        # Validate fallback data through your
        # existing Pydantic schema.
        assessment = (
            LLMScreeningAssessment(
                matched_skills=(
                    data.get(
                        "matched_skills"
                    )
                    or []
                ),
                missing_skills=(
                    data.get(
                        "missing_skills"
                    )
                    or []
                ),
                strengths=(
                    data.get(
                        "strengths"
                    )
                    or []
                ),
                concerns=(
                    data.get(
                        "concerns"
                    )
                    or []
                ),
                reasoning=(
                    data.get(
                        "reasoning"
                    )
                    or ""
                ),
            )
        )

    # --------------------------------------------------
    # IMPORTANT:
    # Your deterministic Python scoring remains unchanged.
    # --------------------------------------------------

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