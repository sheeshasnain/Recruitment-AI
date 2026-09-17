import json

from pydantic import BaseModel, Field

from backend.services.llm_service import get_llm


class CalendarEventDraft(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=500,
    )

    description: str = Field(
        min_length=1,
    )

    candidate_message: str = Field(
        min_length=1,
    )


async def prepare_calendar_event(
    *,
    candidate_name: str,
    job_title: str,
    scheduled_start: str,
    scheduled_end: str,
    timezone: str,
) -> CalendarEventDraft:

    llm = get_llm(
        temperature=0
    )

    prompt = f"""
You are an interview scheduling assistant.

Prepare a professional calendar event draft
for a job interview.

CANDIDATE
Name: {candidate_name}

JOB
Title: {job_title}

SCHEDULE
Start: {scheduled_start}
End: {scheduled_end}
Timezone: {timezone}

Create:

1. A concise calendar event title.
2. A professional calendar event description.
3. A short candidate-facing scheduling message.

IMPORTANT RULES:

- Do NOT change the supplied date.
- Do NOT change the supplied start time.
- Do NOT change the supplied end time.
- Do NOT change the supplied timezone.
- Do NOT invent a company name.
- Do NOT invent interview panel members.
- Do NOT invent interviewer names.
- Do NOT invent a meeting link.
- Do NOT claim an email has already been sent.
- Do NOT claim a calendar event has already been created.
- Do NOT make hiring promises.
- Do NOT include protected characteristics.
- Use only the information provided above.

Return exactly these fields:

title
description
candidate_message
"""

    # ==================================================
    # ATTEMPT 1
    # Groq structured output
    # ==================================================

    try:

        structured_llm = (
            llm.with_structured_output(
                CalendarEventDraft
            )
        )

        draft = await structured_llm.ainvoke(
            prompt
        )

        return draft

    except Exception as structured_error:

        # ==============================================
        # FALLBACK
        #
        # Some Groq models sometimes generate the
        # correct answer without making the structured
        # tool call expected by LangChain.
        # ==============================================

        print(
            "Structured scheduling output failed."
        )

        print(
            "Using JSON fallback."
        )

        print(
            f"Error: {structured_error}"
        )

        fallback_prompt = f"""
{prompt}

The structured-output mechanism is unavailable.

Return ONLY one valid JSON object.

Do not use Markdown.
Do not use code fences.
Do not include any explanation outside the JSON.

Return exactly this structure:

{{
    "title": "",
    "description": "",
    "candidate_message": ""
}}

All three fields must contain strings.

Remember:

- Do not invent company information.
- Do not invent interviewer names.
- Do not invent interview panel members.
- Do not invent a meeting link.
- Keep the supplied date and time unchanged.
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

        content = str(content).strip()

        # ----------------------------------------------
        # Remove accidental Markdown code fences
        # ----------------------------------------------

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

        # ----------------------------------------------
        # Find JSON object
        # ----------------------------------------------

        json_start = content.find("{")
        json_end = content.rfind("}")

        if (
            json_start == -1
            or json_end == -1
        ):
            raise ValueError(
                "Groq scheduling fallback did "
                "not return a JSON object."
            )

        json_text = content[
            json_start:json_end + 1
        ]

        data = json.loads(
            json_text
        )

        # ----------------------------------------------
        # Validate using Pydantic
        # ----------------------------------------------

        return CalendarEventDraft(
            title=data.get("title") or (
                f"Interview - {job_title}"
            ),
            description=(
                data.get("description")
                or
                f"Interview for the "
                f"{job_title} position."
            ),
            candidate_message=(
                data.get("candidate_message")
                or
                f"Your interview for the "
                f"{job_title} position has "
                f"been scheduled."
            ),
        )