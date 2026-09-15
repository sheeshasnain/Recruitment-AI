from backend.schemas.interview import (
    InterviewQuestionSet,
)
from backend.services.llm_service import get_llm


async def generate_interview_questions(
    *,
    job_title: str,
    job_description: str,
    required_skills: list[str],
    candidate_skills: list[str],
    candidate_summary: str,
    screening_strengths: list[str],
    screening_concerns: list[str],
    number_of_questions: int,
) -> InterviewQuestionSet:

    llm = get_llm(
        temperature=0.2
    )

    structured_llm = (
        llm.with_structured_output(
            InterviewQuestionSet
        )
    )

    prompt = f"""
You are an interview preparation specialist.

Create a structured professional interview for
the candidate and job below.

Generate exactly {number_of_questions} questions.

JOB

Title:
{job_title}

Description:
{job_description}

Required skills:
{", ".join(required_skills)}


CANDIDATE

Skills:
{", ".join(candidate_skills)}

Experience:
{candidate_summary}


SCREENING

Strengths:
{", ".join(screening_strengths)}

Concerns:
{", ".join(screening_concerns)}


RULES

1. Questions must be directly job relevant.
2. Do not ask about protected characteristics.
3. Do not ask about age, religion, marital status,
   ethnicity, disability, nationality, political views
   or other sensitive personal characteristics.
4. Include a balanced mixture of technical,
   experience, problem-solving, behavioral and
   role-specific questions.
5. Probe screening concerns where appropriate.
6. Do not assume experience not supported by the CV.
7. Each question must have expected evaluation points.
8. Avoid duplicate questions.
9. Questions should require meaningful answers rather
   than simple yes/no responses.
10. Return exactly {number_of_questions} questions.
"""

    result = await structured_llm.ainvoke(
        prompt
    )

    return result