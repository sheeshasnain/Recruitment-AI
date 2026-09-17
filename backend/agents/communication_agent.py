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

    llm = get_llm(temperature=0)

    structured_llm = llm.with_structured_output(
        EmailDraft
    )

    prompt = f"""
You are a recruitment communication assistant.

Prepare a professional candidate email.

Communication type:
{communication_type}

Candidate:
{candidate_name}

Job:
{job_title}

Interview start:
{scheduled_start or "Not applicable"}

Timezone:
{timezone or "Not applicable"}

Meeting link:
{meeting_link or "Not applicable"}

RULES

1. Write a concise professional email.
2. Do not invent company details.
3. Do not invent dates, times or links.
4. Use only the information provided.
5. Do not mention AI.
6. Do not make hiring promises.
7. Do not include protected or sensitive information.
8. Return only the structured email draft.
"""

    return await structured_llm.ainvoke(prompt)