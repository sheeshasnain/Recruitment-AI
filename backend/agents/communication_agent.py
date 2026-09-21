import json

from backend.schemas.communication import EmailDraft
from backend.services.llm_service import get_llm


async def generate_candidate_email(
    *,
    communication_type: str,
    candidate_name: str,
    job_title: str,
    scheduled_start: str | None = None,
    timezone: str | None = None,
    meeting_link: str | None = None,
) -> EmailDraft:

    llm = get_llm(
        temperature=0
    )

    prompt = f"""
You are a recruitment communication assistant.

Prepare a professional candidate email.

COMMUNICATION TYPE
{communication_type}

CANDIDATE
{candidate_name}

JOB
{job_title}

INTERVIEW START
{scheduled_start or "Not applicable"}

TIMEZONE
{timezone or "Not applicable"}

MEETING LINK
{meeting_link or "Not applicable"}

RULES

1. Write a concise professional email.
2. Do not invent company details.
3. Do not invent dates, times or links.
4. Use only the information provided.
5. Do not mention AI.
6. Do not make hiring promises.
7. Do not include protected or sensitive information.
8. The subject must be concise and professional.
9. The body must be candidate-facing.
10. Do not claim an email has already been sent.
"""

    # ==============================================
    # ATTEMPT 1 — STRUCTURED OUTPUT
    # ==============================================

    try:

        structured_llm = (
            llm.with_structured_output(
                EmailDraft
            )
        )

        return await structured_llm.ainvoke(
            prompt
        )

    except Exception as structured_error:

        print(
            "Structured communication output failed."
        )

        print(
            "Using JSON fallback."
        )

        print(
            f"Error: {structured_error}"
        )

        # ==========================================
        # FALLBACK — STRICT JSON
        # ==========================================

        fallback_prompt = f"""
{prompt}

The structured-output mechanism is unavailable.

Return ONLY one valid JSON object.

Do not use Markdown.
Do not use code fences.
Do not include explanations outside JSON.

Return exactly:

{{
    "subject": "",
    "body": ""
}}

Both fields must contain strings.
"""

        response = await llm.ainvoke(
            fallback_prompt
        )

        content = response.content

        if isinstance(content, list):

            content = "".join(
                str(item)
                for item in content
            )

        content = str(
            content
        ).strip()

        # ==========================================
        # REMOVE CODE FENCES
        # ==========================================

        if content.startswith(
            "```json"
        ):

            content = content[
                len("```json"):
            ].strip()

        elif content.startswith(
            "```"
        ):

            content = content[
                len("```"):
            ].strip()

        if content.endswith(
            "```"
        ):

            content = content[
                :-3
            ].strip()

        # ==========================================
        # FIND JSON
        # ==========================================

        json_start = content.find(
            "{"
        )

        json_end = content.rfind(
            "}"
        )

        if (
            json_start == -1
            or json_end == -1
        ):

            raise ValueError(
                "Groq communication fallback "
                "did not return valid JSON."
            )

        json_text = content[
            json_start:json_end + 1
        ]

        data = json.loads(
            json_text
        )

        return EmailDraft(
            subject=(
                data.get("subject")
                or
                f"Regarding your application "
                f"for {job_title}"
            ),
            body=(
                data.get("body")
                or
                f"Hello {candidate_name},\n\n"
                f"We are contacting you regarding "
                f"your application for the "
                f"{job_title} position."
            ),
        )