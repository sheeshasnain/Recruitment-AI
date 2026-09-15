from backend.schemas.evaluation import (
    InterviewSemanticEvaluation,
)
from backend.services.llm_service import get_llm


async def evaluate_interview(
    *,
    job_title: str,
    required_skills: list[str],
    interview_transcript: str,
) -> InterviewSemanticEvaluation:

    llm = get_llm(
        temperature=0
    )

    structured_llm = (
        llm.with_structured_output(
            InterviewSemanticEvaluation
        )
    )

    prompt = f"""
You are an interview evaluation assistant.

Evaluate the interview using only job-relevant
evidence contained in the transcript.

JOB

Title:
{job_title}

Required skills:
{", ".join(required_skills)}


INTERVIEW TRANSCRIPT

{interview_transcript}


Evaluate four dimensions from 0 to 100:

technical:
demonstrated job-relevant technical knowledge

communication:
clarity, structure and ability to explain answers

problem_solving:
reasoning, approach and handling of scenarios

experience:
quality and relevance of demonstrated examples


RULES

- Use only evidence in the interview.
- Missing evidence should not be invented.
- Do not consider protected characteristics.
- Do not make a hiring decision.
- Do not calculate an overall score.
- Explain strengths and concerns using job-related evidence.
"""

    result = await structured_llm.ainvoke(
        prompt
    )

    result.strengths = (
        result.strengths or []
    )

    result.concerns = (
        result.concerns or []
    )

    return result