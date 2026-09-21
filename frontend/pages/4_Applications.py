import streamlit as st

from frontend.api_client import (
    get_applications,
    get_interviews,
    get_interview,
    make_recruiter_decision,
    make_final_recruiter_decision,
)


st.set_page_config(
    page_title="Applications | Recruitment AI",
    page_icon="📋",
    layout="wide",
)


st.title("📋 Applications")

st.caption(
    "Review AI screening results, manage recruiter "
    "decisions, and record final hiring outcomes."
)


# ==================================================
# HELPERS
# ==================================================


def show_error(message, exc):
    st.error(message)

    try:
        st.json(
            exc.response.json()
        )

    except Exception:
        st.exception(exc)


def format_label(value):
    if value is None:
        return "-"

    return (
        str(value)
        .replace("_", " ")
        .title()
    )


def score_text(value):
    if value is None:
        return "-"

    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return str(value)


def show_list(items, empty_message):
    if items:
        for item in items:
            st.write(f"• {item}")
    else:
        st.caption(empty_message)


# ==================================================
# LOAD APPLICATIONS
# ==================================================

try:
    applications = get_applications()

except Exception as exc:
    show_error(
        "Could not load applications.",
        exc,
    )
    st.stop()


if not applications:
    st.info(
        "No applications found. Screen a candidate "
        "against a job to create an application."
    )
    st.stop()


# ==================================================
# LOAD INTERVIEWS
# ==================================================

try:
    interviews = get_interviews()

except Exception:
    interviews = []


interview_by_application = {
    interview.get("application_id"): interview
    for interview in interviews
    if interview.get("application_id") is not None
}


# ==================================================
# DASHBOARD METRICS
# ==================================================

total_count = len(applications)

screening_complete_count = sum(
    1
    for app in applications
    if app.get("status") == "screening_complete"
)

interview_count = sum(
    1
    for app in applications
    if app.get("approved_for_interview") is True
)

hired_count = sum(
    1
    for app in applications
    if (
        app.get("final_decision") == "hire"
        or app.get("status") == "hired"
    )
)


metric1, metric2, metric3, metric4 = st.columns(4)


with metric1:
    st.metric(
        "Total Applications",
        total_count,
    )


with metric2:
    st.metric(
        "Awaiting Review",
        screening_complete_count,
    )


with metric3:
    st.metric(
        "Interview Approved",
        interview_count,
    )


with metric4:
    st.metric(
        "Hired",
        hired_count,
    )


# ==================================================
# FILTERS
# ==================================================

st.divider()

st.subheader("Application Pipeline")


status_values = sorted(
    {
        str(app.get("status"))
        for app in applications
        if app.get("status")
    }
)


filter_col1, filter_col2 = st.columns(
    [1, 2]
)


with filter_col1:

    selected_status = st.selectbox(
        "Status",
        options=[
            "All",
            *status_values,
        ],
    )


with filter_col2:

    search_query = st.text_input(
        "Search",
        placeholder=(
            "Search candidate, job or application ID..."
        ),
    )


filtered_applications = applications


if selected_status != "All":

    filtered_applications = [
        app
        for app in filtered_applications
        if app.get("status") == selected_status
    ]


if search_query.strip():

    query = search_query.strip().lower()

    filtered_applications = [
        app
        for app in filtered_applications
        if (
            query in str(
                app.get("id", "")
            ).lower()
            or query in str(
                app.get(
                    "candidate_name",
                    "",
                )
            ).lower()
            or query in str(
                app.get(
                    "candidate_email",
                    "",
                )
            ).lower()
            or query in str(
                app.get(
                    "job_title",
                    "",
                )
            ).lower()
        )
    ]


st.caption(
    f"Showing {len(filtered_applications)} "
    f"of {len(applications)} applications."
)


if not filtered_applications:

    st.info(
        "No applications match the selected filters."
    )
    st.stop()


# ==================================================
# APPLICATION TABLE
# ==================================================

table_rows = []


for app in filtered_applications:

    table_rows.append(
        {
            "ID": app.get("id"),
            "Candidate": (
                app.get("candidate_name")
                or "Unknown"
            ),
            "Job": (
                app.get("job_title")
                or "Unknown"
            ),
            "Score": score_text(
                app.get("overall_score")
            ),
            "AI Route": format_label(
                app.get("screening_route")
            ),
            "Status": format_label(
                app.get("status")
            ),
            "Interview": (
                "Approved"
                if app.get(
                    "approved_for_interview"
                )
                else "-"
            ),
            "Final Decision": format_label(
                app.get("final_decision")
            ),
        }
    )


st.dataframe(
    table_rows,
    use_container_width=True,
    hide_index=True,
)


# ==================================================
# SELECT APPLICATION
# ==================================================

st.divider()

st.subheader("Application Review")


application_options = {}


for app in filtered_applications:

    application_id = app.get("id")

    candidate_name = (
        app.get("candidate_name")
        or "Unknown Candidate"
    )

    job_title = (
        app.get("job_title")
        or "Unknown Job"
    )

    status = format_label(
        app.get("status")
    )

    label = (
        f"#{application_id} — "
        f"{candidate_name} — "
        f"{job_title} [{status}]"
    )

    application_options[label] = app


selected_label = st.selectbox(
    "Select Application",
    options=list(
        application_options.keys()
    ),
)


selected_application = (
    application_options[selected_label]
)


application_id = (
    selected_application.get("id")
)


# ==================================================
# APPLICATION OVERVIEW
# ==================================================

st.markdown("### Candidate & Job")


info1, info2, info3, info4 = st.columns(4)


with info1:
    st.write("**Candidate**")
    st.write(
        selected_application.get(
            "candidate_name"
        )
        or "Unknown"
    )


with info2:
    st.write("**Email**")
    st.write(
        selected_application.get(
            "candidate_email"
        )
        or "-"
    )


with info3:
    st.write("**Position**")
    st.write(
        selected_application.get(
            "job_title"
        )
        or "Unknown"
    )


with info4:
    st.write("**Status**")
    st.write(
        format_label(
            selected_application.get(
                "status"
            )
        )
    )


# ==================================================
# AI SCREENING
# ==================================================

st.divider()

st.markdown("### AI Screening")


score1, score2, score3, score4 = st.columns(4)


with score1:
    st.metric(
        "Overall Score",
        score_text(
            selected_application.get(
                "overall_score"
            )
        ),
    )


with score2:
    st.metric(
        "Skills Score",
        score_text(
            selected_application.get(
                "skills_score"
            )
        ),
    )


with score3:
    st.metric(
        "Experience Score",
        score_text(
            selected_application.get(
                "experience_score"
            )
        ),
    )


with score4:
    st.metric(
        "AI Route",
        format_label(
            selected_application.get(
                "screening_route"
            )
        ),
    )


screen_col1, screen_col2 = st.columns(2)


with screen_col1:

    st.write("**Matched Skills**")

    show_list(
        selected_application.get(
            "matched_skills"
        )
        or [],
        "No matched skills recorded.",
    )


    st.write("**Strengths**")

    show_list(
        selected_application.get(
            "strengths"
        )
        or [],
        "No strengths recorded.",
    )


with screen_col2:

    st.write("**Missing Skills**")

    show_list(
        selected_application.get(
            "missing_skills"
        )
        or [],
        "No missing skills recorded.",
    )


    st.write("**Concerns**")

    show_list(
        selected_application.get(
            "concerns"
        )
        or [],
        "No concerns recorded.",
    )


reasoning = selected_application.get(
    "reasoning"
)


if reasoning:

    with st.expander(
        "Screening Reasoning"
    ):
        st.write(reasoning)


st.caption(
    "AI screening provides decision support. "
    "The recruiter controls interview approval."
)


# ==================================================
# FIRST RECRUITER DECISION
# ==================================================

st.divider()

st.markdown("### Recruiter Screening Decision")


application_status = (
    selected_application.get(
        "status"
    )
)


recruiter_decision = (
    selected_application.get(
        "recruiter_decision"
    )
)


if application_status == "screening_complete":

    st.warning(
        "This application is awaiting recruiter review."
    )


    recruiter_notes = st.text_area(
        "Recruiter Notes",
        placeholder=(
            "Add notes about the screening review..."
        ),
        key=(
            f"screening_notes_{application_id}"
        ),
    )


    approve_col, hold_col, reject_col = (
        st.columns(3)
    )


    with approve_col:

        if st.button(
            "Approve for Interview",
            type="primary",
            use_container_width=True,
            key=(
                f"approve_{application_id}"
            ),
        ):

            try:
                make_recruiter_decision(
                    application_id=application_id,
                    decision="approve",
                    notes=(
                        recruiter_notes.strip()
                        or None
                    ),
                )

                st.success(
                    "Candidate approved for interview."
                )

                st.rerun()

            except Exception as exc:
                show_error(
                    "Could not approve application.",
                    exc,
                )


    with hold_col:

        if st.button(
            "Place on Hold",
            use_container_width=True,
            key=(
                f"hold_{application_id}"
            ),
        ):

            try:
                make_recruiter_decision(
                    application_id=application_id,
                    decision="hold",
                    notes=(
                        recruiter_notes.strip()
                        or None
                    ),
                )

                st.success(
                    "Application placed on hold."
                )

                st.rerun()

            except Exception as exc:
                show_error(
                    "Could not place application on hold.",
                    exc,
                )


    with reject_col:

        if st.button(
            "Reject",
            use_container_width=True,
            key=(
                f"reject_{application_id}"
            ),
        ):

            try:
                make_recruiter_decision(
                    application_id=application_id,
                    decision="reject",
                    notes=(
                        recruiter_notes.strip()
                        or None
                    ),
                )

                st.success(
                    "Application rejected."
                )

                st.rerun()

            except Exception as exc:
                show_error(
                    "Could not reject application.",
                    exc,
                )


else:

    decision_col1, decision_col2 = (
        st.columns(2)
    )


    with decision_col1:

        st.write(
            "**Recruiter Decision:**",
            format_label(
                recruiter_decision
            ),
        )


    with decision_col2:

        st.write(
            "**Approved for Interview:**",
            (
                "Yes"
                if selected_application.get(
                    "approved_for_interview"
                )
                else "No"
            ),
        )


    recruiter_notes = (
        selected_application.get(
            "recruiter_notes"
        )
    )


    if recruiter_notes:

        st.write(
            "**Recruiter Notes:**"
        )

        st.write(
            recruiter_notes
        )


# ==================================================
# INTERVIEW
# ==================================================

st.divider()

st.markdown("### Interview")


interview_summary = (
    interview_by_application.get(
        application_id
    )
)


if not interview_summary:

    if selected_application.get(
        "approved_for_interview"
    ):

        st.info(
            "Candidate is approved for interview. "
            "Prepare the interview from the "
            "Interviews page."
        )

    else:

        st.caption(
            "No interview has been created "
            "for this application."
        )


else:

    interview_id = (
        interview_summary.get(
            "interview_id"
        )
        or interview_summary.get("id")
    )


    interview_status = (
        interview_summary.get(
            "status"
        )
        or "unknown"
    )


    interview_col1, interview_col2 = (
        st.columns(2)
    )


    with interview_col1:

        st.write(
            "**Interview ID:**",
            interview_id,
        )


    with interview_col2:

        st.write(
            "**Interview Status:**",
            format_label(
                interview_status
            ),
        )


# ==================================================
# INTERVIEW EVALUATION
# ==================================================

evaluation = None


if interview_summary:

    try:
        interview_details = get_interview(
            interview_id
        )

        evaluation = (
            interview_details.get(
                "evaluation"
            )
            if interview_details
            else None
        )

    except Exception:
        interview_details = None
        evaluation = None


if evaluation:

    st.markdown(
        "#### Interview Evaluation"
    )


    eval1, eval2, eval3, eval4, eval5 = (
        st.columns(5)
    )


    with eval1:
        st.metric(
            "Overall",
            score_text(
                evaluation.get(
                    "overall_score"
                )
            ),
        )


    with eval2:
        st.metric(
            "Technical",
            score_text(
                evaluation.get(
                    "technical_score"
                )
            ),
        )


    with eval3:
        st.metric(
            "Problem Solving",
            score_text(
                evaluation.get(
                    "problem_solving_score"
                )
            ),
        )


    with eval4:
        st.metric(
            "Experience",
            score_text(
                evaluation.get(
                    "experience_score"
                )
            ),
        )


    with eval5:
        st.metric(
            "Communication",
            score_text(
                evaluation.get(
                    "communication_score"
                )
            ),
        )


    st.write(
        "**AI Recommendation:**",
        format_label(
            evaluation.get(
                "recommendation"
            )
        ),
    )


    eval_col1, eval_col2 = st.columns(2)


    with eval_col1:

        st.write(
            "**Interview Strengths**"
        )

        show_list(
            evaluation.get(
                "strengths"
            )
            or [],
            "No strengths recorded.",
        )


    with eval_col2:

        st.write(
            "**Interview Concerns**"
        )

        show_list(
            evaluation.get(
                "concerns"
            )
            or [],
            "No concerns recorded.",
        )


    if evaluation.get("summary"):

        st.write(
            "**Evaluation Summary**"
        )

        st.write(
            evaluation.get(
                "summary"
            )
        )


    st.caption(
        "Interview evaluation is AI-generated "
        "decision support. The recruiter makes "
        "the final hiring decision."
    )


elif interview_summary:

    st.info(
        "No interview evaluation is available yet."
    )


# ==================================================
# FINAL RECRUITER DECISION
# ==================================================

st.divider()

st.markdown("### Final Recruiter Decision")


final_decision = (
    selected_application.get(
        "final_decision"
    )
)


if final_decision:

    st.success(
        "Final recruiter decision recorded."
    )


    final_col1, final_col2 = st.columns(2)


    with final_col1:

        st.write(
            "**Decision:**",
            format_label(
                final_decision
            ),
        )

        st.write(
            "**Application Status:**",
            format_label(
                selected_application.get(
                    "status"
                )
            ),
        )


    with final_col2:

        st.write(
            "**Decision Date:**",
            selected_application.get(
                "final_decision_at"
            )
            or "-",
        )


    st.write(
        "**Decision Notes:**"
    )

    st.write(
        selected_application.get(
            "final_decision_notes"
        )
        or "No notes recorded."
    )


elif not interview_summary:

    st.info(
        "A final decision becomes available "
        "after the candidate completes an "
        "interview and receives an evaluation."
    )


elif not evaluation:

    st.info(
        "Complete and evaluate the interview "
        "before recording a final decision."
    )


else:

    st.info(
        "Review the interview evaluation before "
        "recording the final hiring decision."
    )


    final_decision_label = st.selectbox(
        "Final Decision",
        options=[
            "Hire",
            "Hold",
            "Reject",
        ],
        key=(
            f"final_decision_{application_id}"
        ),
    )


    final_decision_map = {
        "Hire": "hire",
        "Hold": "hold",
        "Reject": "reject",
    }


    final_notes = st.text_area(
        "Final Decision Notes",
        placeholder=(
            "Document the reason for the "
            "final recruiter decision..."
        ),
        height=140,
        key=(
            f"final_notes_{application_id}"
        ),
    )


    st.warning(
        "The final decision cannot be changed "
        "after it is submitted."
    )


    confirmation = st.checkbox(
        (
            "I confirm that I want to record "
            "this final decision."
        ),
        key=(
            f"confirm_final_{application_id}"
        ),
    )


    if st.button(
        "Record Final Decision",
        type="primary",
        use_container_width=True,
        disabled=not confirmation,
        key=(
            f"record_final_{application_id}"
        ),
    ):

        try:

            make_final_recruiter_decision(
                application_id=application_id,
                decision=(
                    final_decision_map[
                        final_decision_label
                    ]
                ),
                notes=(
                    final_notes.strip()
                    or None
                ),
            )

            st.success(
                "Final recruiter decision recorded."
            )

            st.rerun()

        except Exception as exc:

            show_error(
                "Could not record final decision.",
                exc,
            )