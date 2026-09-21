import streamlit as st

from frontend.api_client import (
    get_jobs,
    get_candidates,
    get_applications,
    get_interviews,
    get_schedules,
    get_communications,
    get_tool_logs,
)


st.set_page_config(
    page_title="Dashboard | Recruitment AI",
    page_icon="📊",
    layout="wide",
)


st.title("📊 Recruitment Dashboard")

st.caption(
    "Monitor the recruitment pipeline, interviews, "
    "scheduling, communications, and hiring outcomes."
)


# ==================================================
# HELPERS
# ==================================================


def format_label(value):
    if not value:
        return "-"

    return (
        str(value)
        .replace("_", " ")
        .title()
    )


def load_data(function):
    try:
        return function(), None

    except Exception as exc:
        return [], exc


# ==================================================
# LOAD DATA
# ==================================================

jobs, jobs_error = load_data(
    get_jobs
)

candidates, candidates_error = load_data(
    get_candidates
)

applications, applications_error = load_data(
    get_applications
)

interviews, interviews_error = load_data(
    get_interviews
)

schedules, schedules_error = load_data(
    get_schedules
)

communications, communications_error = load_data(
    get_communications
)

tool_logs, logs_error = load_data(
    get_tool_logs
)


errors = [
    ("Jobs", jobs_error),
    ("Candidates", candidates_error),
    ("Applications", applications_error),
    ("Interviews", interviews_error),
    ("Scheduling", schedules_error),
    ("Communications", communications_error),
    ("Audit Logs", logs_error),
]


failed_services = [
    name
    for name, error in errors
    if error is not None
]


if failed_services:

    st.warning(
        "Some dashboard data could not be loaded: "
        + ", ".join(failed_services)
    )


# ==================================================
# PRIMARY METRICS
# ==================================================

active_jobs = sum(
    1
    for job in jobs
    if job.get("is_active", True)
)


hired_count = sum(
    1
    for app in applications
    if (
        app.get("final_decision") == "hire"
        or app.get("status") == "hired"
    )
)


metric1, metric2, metric3, metric4 = (
    st.columns(4)
)


with metric1:
    st.metric(
        "Active Jobs",
        active_jobs,
    )


with metric2:
    st.metric(
        "Candidates",
        len(candidates),
    )


with metric3:
    st.metric(
        "Applications",
        len(applications),
    )


with metric4:
    st.metric(
        "Hired",
        hired_count,
    )


# ==================================================
# RECRUITER ATTENTION
# ==================================================

st.divider()

st.subheader("Recruiter Attention")


awaiting_screening_review = sum(
    1
    for app in applications
    if app.get("status")
    == "screening_complete"
)


awaiting_interview = sum(
    1
    for app in applications
    if (
        app.get(
            "approved_for_interview"
        )
        is True
        and app.get("status")
        == "interview_approved"
    )
)


awaiting_final_decision = sum(
    1
    for app in applications
    if (
        app.get("status")
        == "evaluation_complete"
        and not app.get(
            "final_decision"
        )
    )
)


pending_schedules = sum(
    1
    for schedule in schedules
    if schedule.get("status")
    == "pending_approval"
)


pending_emails = sum(
    1
    for communication
    in communications
    if communication.get("status")
    == "draft"
)


attention1, attention2, attention3 = (
    st.columns(3)
)


with attention1:

    st.metric(
        "Screening Reviews",
        awaiting_screening_review,
    )

    st.caption(
        "Applications waiting for "
        "recruiter review."
    )


with attention2:

    st.metric(
        "Schedule Approvals",
        pending_schedules,
    )

    st.caption(
        "Interview schedules waiting "
        "for approval."
    )


with attention3:

    st.metric(
        "Email Approvals",
        pending_emails,
    )

    st.caption(
        "Candidate emails waiting "
        "for review."
    )


attention4, attention5 = st.columns(2)


with attention4:

    st.metric(
        "Interviews to Prepare",
        awaiting_interview,
    )

    st.caption(
        "Approved candidates without "
        "a prepared interview."
    )


with attention5:

    st.metric(
        "Final Decisions",
        awaiting_final_decision,
    )

    st.caption(
        "Evaluated candidates awaiting "
        "a final recruiter decision."
    )


# ==================================================
# APPLICATION PIPELINE
# ==================================================

st.divider()

st.subheader("Application Pipeline")


pipeline_statuses = [
    (
        "Screening Complete",
        "screening_complete",
    ),
    (
        "Interview Approved",
        "interview_approved",
    ),
    (
        "Interview Prepared",
        "interview_prepared",
    ),
    (
        "Interview In Progress",
        "interview_in_progress",
    ),
    (
        "Interview Completed",
        "interview_completed",
    ),
    (
        "Evaluation Complete",
        "evaluation_complete",
    ),
    (
        "Hired",
        "hired",
    ),
]


pipeline_columns = st.columns(
    len(pipeline_statuses)
)


for column, (
    label,
    status,
) in zip(
    pipeline_columns,
    pipeline_statuses,
):

    count = sum(
        1
        for app in applications
        if app.get("status") == status
    )

    with column:
        st.metric(
            label,
            count,
        )


# ==================================================
# INTERVIEW OPERATIONS
# ==================================================

st.divider()

st.subheader("Interview Operations")


prepared_interviews = sum(
    1
    for interview in interviews
    if interview.get("status")
    == "prepared"
)


in_progress_interviews = sum(
    1
    for interview in interviews
    if interview.get("status")
    == "in_progress"
)


completed_interviews = sum(
    1
    for interview in interviews
    if interview.get("status")
    == "completed"
)


scheduled_interviews = sum(
    1
    for schedule in schedules
    if schedule.get("status")
    == "scheduled"
)


interview1, interview2, interview3, interview4 = (
    st.columns(4)
)


with interview1:
    st.metric(
        "Prepared",
        prepared_interviews,
    )


with interview2:
    st.metric(
        "In Progress",
        in_progress_interviews,
    )


with interview3:
    st.metric(
        "Completed",
        completed_interviews,
    )


with interview4:
    st.metric(
        "Scheduled",
        scheduled_interviews,
    )


# ==================================================
# COMMUNICATION + TOOLS
# ==================================================

st.divider()

left_column, right_column = (
    st.columns(2)
)


with left_column:

    st.subheader(
        "Candidate Communications"
    )


    sent_emails = sum(
        1
        for communication
        in communications
        if communication.get("status")
        == "sent"
    )


    rejected_emails = sum(
        1
        for communication
        in communications
        if communication.get("status")
        == "rejected"
    )


    comm1, comm2, comm3 = (
        st.columns(3)
    )


    with comm1:
        st.metric(
            "Drafts",
            pending_emails,
        )


    with comm2:
        st.metric(
            "Sent",
            sent_emails,
        )


    with comm3:
        st.metric(
            "Rejected",
            rejected_emails,
        )


with right_column:

    st.subheader(
        "External Tool Health"
    )


    successful_actions = sum(
        1
        for log in tool_logs
        if log.get("status")
        == "success"
    )


    failed_actions = sum(
        1
        for log in tool_logs
        if log.get("status")
        == "failed"
    )


    tool1, tool2, tool3 = (
        st.columns(3)
    )


    with tool1:
        st.metric(
            "Actions",
            len(tool_logs),
        )


    with tool2:
        st.metric(
            "Successful",
            successful_actions,
        )


    with tool3:
        st.metric(
            "Failed",
            failed_actions,
        )


# ==================================================
# RECENT APPLICATIONS
# ==================================================

st.divider()

st.subheader("Recent Applications")


if not applications:

    st.info(
        "No applications have been "
        "created yet."
    )


else:

    recent_applications = (
        applications[:5]
    )


    recent_rows = []


    for app in recent_applications:

        score = app.get(
            "overall_score"
        )

        if score is not None:
            try:
                score = (
                    f"{float(score):.1f}"
                )
            except (
                TypeError,
                ValueError,
            ):
                pass

        else:
            score = "-"


        recent_rows.append(
            {
                "ID": app.get("id"),
                "Candidate": (
                    app.get(
                        "candidate_name"
                    )
                    or "Unknown"
                ),
                "Position": (
                    app.get(
                        "job_title"
                    )
                    or "Unknown"
                ),
                "Score": score,
                "AI Route": (
                    format_label(
                        app.get(
                            "screening_route"
                        )
                    )
                ),
                "Status": (
                    format_label(
                        app.get(
                            "status"
                        )
                    )
                ),
                "Final Decision": (
                    format_label(
                        app.get(
                            "final_decision"
                        )
                    )
                ),
            }
        )


    st.dataframe(
        recent_rows,
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# HUMAN CONTROL NOTE
# ==================================================

st.divider()

st.caption(
    "AI agents support screening, interview "
    "preparation, evaluation, scheduling drafts, "
    "and communication drafts. Recruiters retain "
    "control over interview approvals, external "
    "tool actions, and final hiring decisions."
)