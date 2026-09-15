from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from backend.agents.interview_preparation_agent import (
    generate_interview_questions,
)
from backend.agents.interview_state import (
    InterviewState,
)


async def prepare_interview_node(
    state: InterviewState,
) -> dict:

    questions = (
        await generate_interview_questions(
            job_title=state["job_title"],
            job_description=(
                state["job_description"]
            ),
            required_skills=(
                state["required_skills"]
            ),
            candidate_skills=(
                state["candidate_skills"]
            ),
            candidate_summary=(
                state["candidate_summary"]
            ),
            screening_strengths=(
                state["screening_strengths"]
            ),
            screening_concerns=(
                state["screening_concerns"]
            ),
            number_of_questions=(
                state["number_of_questions"]
            ),
        )
    )

    return {
        "generated_questions": questions,
        "status": "prepared",
    }


builder = StateGraph(
    InterviewState
)

builder.add_node(
    "prepare_interview",
    prepare_interview_node,
)

builder.add_edge(
    START,
    "prepare_interview",
)

builder.add_edge(
    "prepare_interview",
    END,
)

interview_preparation_graph = (
    builder.compile()
)