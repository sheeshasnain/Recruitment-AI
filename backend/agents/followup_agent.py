import json

from backend.schemas.interview import FollowUpQuestion
from backend.services.llm_service import get_llm


async def generate_followup_question(
    *,
    original_question: str,
    candidate_answer: str,
    expected_points: list[str],
) -> FollowUpQuestion:

    llm = get_llm(
        temperature=0
    )

    # ---------------------------------------------------------
    # PRIMARY METHOD
    # Groq structured output
    # ---------------------------------------------------------

    structured_llm = llm.with_structured_output(
        FollowUpQuestion
    )

    expected_points_text = (
        ", ".join(expected_points)
        if expected_points
        else "No specific expected points provided."
    )

    prompt = f"""
You are assisting a recruiter during a structured
job interview.

Your job is to generate exactly ONE job-relevant
follow-up question.

ORIGINAL QUESTION:

{original_question}


CANDIDATE ANSWER:

{candidate_answer}


EXPECTED EVALUATION POINTS:

{expected_points_text}


Generate a follow-up question only when it helps:

- clarify an incomplete answer,
- probe technical depth,
- request a concrete example,
- explore an important missing job-related point.

IMPORTANT RULES:

1. Return exactly one follow-up question.
2. Do not repeat the original question.
3. Keep the question directly relevant to the job interview.
4. Do not ask about protected or sensitive characteristics.
5. Do not make a hiring decision.
6. Provide a short reason explaining why the follow-up is useful.

You MUST return data matching this structure:

question: string
reason: string

Both fields are REQUIRED.
Neither field may be null.
Do not return markdown.
Do not return headings.
Do not return additional fields.
"""

    try:
        result = await structured_llm.ainvoke(
            prompt
        )

        return result

    except Exception as structured_error:

        print(
            "Structured follow-up generation failed:",
            structured_error,
        )

        # -----------------------------------------------------
        # FALLBACK METHOD
        # Ask Groq for plain JSON instead of tool calling.
        # -----------------------------------------------------

        fallback_prompt = f"""
You are assisting a recruiter during a structured
job interview.

ORIGINAL QUESTION:

{original_question}


CANDIDATE ANSWER:

{candidate_answer}


EXPECTED EVALUATION POINTS:

{expected_points_text}


Generate exactly ONE useful job-relevant follow-up
question.

The follow-up should clarify missing information,
probe technical depth, request a concrete example,
or explore an important missing job-related point.

Do not ask about protected or sensitive personal
characteristics.

Return ONLY valid JSON.

The JSON must have exactly these two fields:

{{
    "question": "your follow-up question",
    "reason": "short explanation of why this follow-up is useful"
}}

Do not use markdown.
Do not use ```json.
Do not include any text before or after the JSON.
"""

        response = await llm.ainvoke(
            fallback_prompt
        )

        content = response.content

        # Some model/provider responses may return
        # content as a list rather than a simple string.
        if isinstance(content, list):
            content = "".join(
                str(item)
                for item in content
            )

        content = str(content).strip()

        # Remove accidental markdown fences if Groq
        # ignores the instruction.
        if content.startswith("```json"):
            content = content[7:]

        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        try:
            data = json.loads(content)

            return FollowUpQuestion(
                question=data["question"],
                reason=data["reason"],
            )

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
        ) as fallback_error:

            print(
                "Fallback follow-up parsing failed:",
                fallback_error,
            )

            raise RuntimeError(
                "Unable to generate a valid "
                "follow-up question."
            ) from structured_error