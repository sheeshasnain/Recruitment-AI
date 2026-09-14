from langgraph.graph import END, START, StateGraph

from backend.agents.intake_agent import candidate_intake_agent
from backend.agents.screening_agent import (
    determine_screening_route,
    screening_agent,
)
from backend.agents.state import RecruitmentState


# ---------------------------------------------------------
# FINAL ROUTE NODES
# ---------------------------------------------------------

def shortlist_node(state: RecruitmentState) -> dict:
    """
    Handles candidates who passed the screening threshold.

    Later this node will connect to:
    - Human recruiter approval
    - Scheduling Agent
    - Google Calendar

    For now it simply marks the workflow outcome.
    """

    return {
        "route": "shortlist"
    }


def manual_review_node(state: RecruitmentState) -> dict:
    """
    Handles candidates whose score is not strong enough for
    automatic shortlisting but is also not a clear rejection.

    Later the recruiter will manually review these candidates.
    """

    return {
        "route": "manual_review"
    }


def reject_node(state: RecruitmentState) -> dict:
    """
    Handles candidates whose score falls below the screening
    threshold.

    Later this node will connect to:
    - Human approval
    - Communication Agent
    - Rejection email workflow

    The system should not automatically send rejection emails.
    """

    return {
        "route": "reject"
    }


# ---------------------------------------------------------
# CONDITIONAL ROUTER
# ---------------------------------------------------------

def route_candidate(state: RecruitmentState) -> str:
    """
    Reads the route calculated by determine_screening_route()
    and tells LangGraph which node should run next.
    """

    return state["route"]


# ---------------------------------------------------------
# CREATE THE LANGGRAPH
# ---------------------------------------------------------

builder = StateGraph(RecruitmentState)


# ---------------------------------------------------------
# REGISTER AGENT / WORKFLOW NODES
# ---------------------------------------------------------

builder.add_node(
    "candidate_intake",
    candidate_intake_agent,
)

builder.add_node(
    "screen_candidate",
    screening_agent,
)

builder.add_node(
    "determine_route",
    determine_screening_route,
)

builder.add_node(
    "shortlist",
    shortlist_node,
)

builder.add_node(
    "manual_review",
    manual_review_node,
)

builder.add_node(
    "reject",
    reject_node,
)


# ---------------------------------------------------------
# DEFINE NORMAL WORKFLOW EDGES
# ---------------------------------------------------------

# Workflow begins with candidate intake
builder.add_edge(
    START,
    "candidate_intake",
)


# After resume extraction / candidate profiling,
# send the candidate to the screening agent
builder.add_edge(
    "candidate_intake",
    "screen_candidate",
)


# After screening, calculate the deterministic system route
builder.add_edge(
    "screen_candidate",
    "determine_route",
)


# ---------------------------------------------------------
# CONDITIONAL ROUTING
# ---------------------------------------------------------

builder.add_conditional_edges(
    "determine_route",
    route_candidate,
    {
        "shortlist": "shortlist",
        "manual_review": "manual_review",
        "reject": "reject",
    },
)


# ---------------------------------------------------------
# END WORKFLOW
# ---------------------------------------------------------

builder.add_edge(
    "shortlist",
    END,
)

builder.add_edge(
    "manual_review",
    END,
)

builder.add_edge(
    "reject",
    END,
)


# ---------------------------------------------------------
# COMPILE GRAPH
# ---------------------------------------------------------

recruitment_graph = builder.compile()