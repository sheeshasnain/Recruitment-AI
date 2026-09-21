import streamlit as st

from frontend.api_client import (
    complete_interview,
    evaluate_interview,
    generate_interview_followup,
    get_applications,
    get_interview,
    get_interview_questions,
    get_interviews,
    prepare_interview,
    start_interview,
    submit_interview_answer,
)


st.set_page_config(
    page_title="Interviews | Recruitment AI",
    page_icon="🎙️",
    layout="wide",
)


st.title("🎙️ Interviews")

st.caption(
    "Prepare, conduct, complete, and evaluate "
    "structured candidate interviews."
)


# ==================================================
# HELPERS
# ==================================================


def refresh_page():
    st.rerun()


def show_error(message, exc):
    st.error(message)

    try:
        detail = exc.response.json()

        st.json(detail)

    except Exception:
        st.exception(exc)


# ==================================================
# LOAD DATA
# ==================================================

try:
    interviews = get_interviews()

except Exception as exc:
    interviews = []

    show_error(
        "Could not load interviews.",
        exc,
    )


try:
    applications = get_applications()

except Exception as exc:
    applications = []

    show_error(
        "Could not load applications.",
        exc,
    )


# ==================================================
# METRICS
# ==================================================

total_interviews = len(interviews)

prepared_count = sum(
    1
    for interview in interviews
    if interview.get("status") == "prepared"
)

in_progress_count = sum(
    1
    for interview in interviews
    if interview.get("status") == "in_progress"
)

completed_count = sum(
    1
    for interview in interviews
    if interview.get("status") == "completed"
)


metric1, metric2, metric3, metric4 = st.columns(4)


with metric1:
    st.metric(
        "Total Interviews",
        total_interviews,
    )


with metric2:
    st.metric(
        "Prepared",
        prepared_count,
    )


with metric3:
    st.metric(
        "In Progress",
        in_progress_count,
    )


with metric4:
    st.metric(
        "Completed",
        completed_count,
    )


# ==================================================
# PREPARE NEW INTERVIEW
# ==================================================

st.divider()

st.subheader("Prepare Interview")

st.caption(
    "Only recruiter-approved applications "
    "can be prepared for interview."
)


approved_applications = [
    application
    for application in applications
    if application.get(
        "approved_for_interview",
        False,
    )
]


existing_application_ids = {
    interview.get("application_id")
    for interview in interviews
}


available_applications = [
    application
    for application in approved_applications
    if application.get("id")
    not in existing_application_ids
]


if not available_applications:

    st.info(
        "No recruiter-approved applications "
        "are currently waiting for interview "
        "preparation."
    )

else:

    application_options = {}

    for application in available_applications:

        application_id = application.get("id")

        candidate_name = application.get(
            "candidate_name",
            "Candidate",
        )

        job_title = application.get(
            "job_title",
            "Job",
        )

        label = (
            str(application_id)
            + " - "
            + str(candidate_name)
            + " - "
            + str(job_title)
        )

        application_options[label] = (
            application
        )


    selected_application_label = (
        st.selectbox(
            "Select Approved Application",
            options=list(
                application_options.keys()
            ),
        )
    )


    number_of_questions = (
        st.slider(
            "Number of Questions",
            min_value=5,
            max_value=15,
            value=8,
        )
    )


    if st.button(
        "Prepare Interview",
        type="primary",
    ):

        selected_application = (
            application_options[
                selected_application_label
            ]
        )

        application_id = (
            selected_application.get("id")
        )

        try:

            with st.spinner(
                "AI is preparing structured "
                "interview questions..."
            ):

                result = prepare_interview(
                    application_id=application_id,
                    number_of_questions=(
                        number_of_questions
                    ),
                )

            st.success(
                "Interview prepared successfully."
            )

            st.write(
                "Interview ID:",
                result.get("interview_id"),
            )

            st.write(
                "Questions Created:",
                result.get(
                    "questions_created"
                ),
            )

            refresh_page()

        except Exception as exc:

            show_error(
                "Could not prepare interview.",
                exc,
            )


# ==================================================
# INTERVIEW LIST
# ==================================================

st.divider()

st.subheader("Interview List")


if not interviews:

    st.info(
        "No interviews have been prepared yet."
    )

    st.stop()


table_data = []


for interview in interviews:

    table_data.append(
        {
            "Interview ID": interview.get(
                "interview_id"
            ),
            "Application ID": interview.get(
                "application_id"
            ),
            "Candidate": interview.get(
                "candidate_name"
            ),
            "Job": interview.get(
                "job_title"
            ),
            "Status": interview.get(
                "status"
            ),
            "Score": interview.get(
                "overall_score"
            ),
            "Recommendation": interview.get(
                "recommendation"
            ),
        }
    )


st.dataframe(
    table_data,
    use_container_width=True,
    hide_index=True,
)


# ==================================================
# SELECT INTERVIEW
# ==================================================

st.divider()

st.subheader("Interview Workspace")


interview_options = {}


for interview in interviews:

    interview_id = interview.get(
        "interview_id"
    )

    candidate_name = interview.get(
        "candidate_name",
        "Candidate",
    )

    job_title = interview.get(
        "job_title",
        "Job",
    )

    status = interview.get(
        "status",
        "unknown",
    )

    label = (
        str(interview_id)
        + " - "
        + str(candidate_name)
        + " - "
        + str(job_title)
        + " ["
        + str(status)
        + "]"
    )

    interview_options[label] = (
        interview_id
    )


selected_interview_label = (
    st.selectbox(
        "Select Interview",
        options=list(
            interview_options.keys()
        ),
    )
)


selected_interview_id = (
    interview_options[
        selected_interview_label
    ]
)


# ==================================================
# LOAD SELECTED INTERVIEW
# ==================================================

try:

    interview_detail = get_interview(
        selected_interview_id
    )

except Exception as exc:

    show_error(
        "Could not load interview details.",
        exc,
    )

    st.stop()


status = interview_detail.get(
    "status"
)


st.write(
    "**Interview ID:**",
    interview_detail.get(
        "interview_id"
    ),
)

st.write(
    "**Application ID:**",
    interview_detail.get(
        "application_id"
    ),
)

st.write(
    "**Status:**",
    status,
)


if interview_detail.get("started_at"):

    st.write(
        "**Started:**",
        interview_detail.get(
            "started_at"
        ),
    )


if interview_detail.get(
    "completed_at"
):

    st.write(
        "**Completed:**",
        interview_detail.get(
            "completed_at"
        ),
    )


# ==================================================
# START INTERVIEW
# ==================================================

if status == "prepared":

    st.info(
        "This interview has been prepared "
        "and is ready to start."
    )

    if st.button(
        "Start Interview",
        type="primary",
    ):

        try:

            result = start_interview(
                selected_interview_id
            )

            st.success(
                "Interview started."
            )

            st.write(
                "Status:",
                result.get("status"),
            )

            refresh_page()

        except Exception as exc:

            show_error(
                "Could not start interview.",
                exc,
            )


# ==================================================
# QUESTIONS
# ==================================================

st.divider()

st.subheader("Interview Questions")


try:

    questions = get_interview_questions(
        selected_interview_id
    )

except Exception as exc:

    questions = []

    show_error(
        "Could not load interview questions.",
        exc,
    )


if not questions:

    st.info(
        "No interview questions found."
    )


for question in questions:

    question_id = question.get("id")

    sequence = question.get(
        "sequence"
    )

    category = question.get(
        "category"
    )

    difficulty = question.get(
        "difficulty"
    )

    is_followup = question.get(
        "is_followup",
        False,
    )


    if is_followup:

        heading = (
            "Follow-up "
            + str(sequence)
        )

    else:

        heading = (
            "Question "
            + str(sequence)
        )


    with st.expander(
        heading
        + " — "
        + str(category),
        expanded=(
            status == "in_progress"
        ),
    ):

        st.markdown(
            "**Question**"
        )

        st.write(
            question.get(
                "question"
            )
        )


        detail1, detail2 = (
            st.columns(2)
        )


        with detail1:

            st.write(
                "**Category:**",
                category,
            )


        with detail2:

            st.write(
                "**Difficulty:**",
                difficulty,
            )


        expected_points = (
            question.get(
                "expected_points",
                [],
            )
            or []
        )


        if expected_points:

            st.write(
                "**Expected Points:**"
            )

            for point in expected_points:

                st.write(
                    "• " + str(point)
                )


        # ------------------------------------------
        # EXISTING ANSWER
        # ------------------------------------------

        existing_answer = None

        detail_questions = (
            interview_detail.get(
                "questions",
                [],
            )
            or []
        )


        for detail_question in (
            detail_questions
        ):

            if (
                detail_question.get(
                    "question_id"
                )
                == question_id
            ):

                existing_answer = (
                    detail_question.get(
                        "answer"
                    )
                )

                break


        if existing_answer:

            st.success(
                "Answer already submitted."
            )

            st.write(
                existing_answer
            )


        # ------------------------------------------
        # ANSWER FORM
        # ------------------------------------------

        if status == "in_progress":

            answer_key = (
                "answer_"
                + str(
                    selected_interview_id
                )
                + "_"
                + str(question_id)
            )

            answer_text = (
                st.text_area(
                    "Candidate Answer",
                    value=(
                        existing_answer
                        or ""
                    ),
                    key=answer_key,
                    height=150,
                )
            )


            button_col1, button_col2 = (
                st.columns(2)
            )


            with button_col1:

                submit_clicked = (
                    st.button(
                        (
                            "Update Answer"
                            if existing_answer
                            else "Submit Answer"
                        ),
                        key=(
                            "submit_"
                            + str(question_id)
                        ),
                    )
                )


                if submit_clicked:

                    if not answer_text.strip():

                        st.warning(
                            "Enter the candidate's "
                            "answer first."
                        )

                    else:

                        try:

                            result = (
                                submit_interview_answer(
                                    interview_id=(
                                        selected_interview_id
                                    ),
                                    question_id=(
                                        question_id
                                    ),
                                    answer=(
                                        answer_text.strip()
                                    ),
                                )
                            )

                            if result.get(
                                "updated"
                            ):

                                st.success(
                                    "Answer updated."
                                )

                            else:

                                st.success(
                                    "Answer submitted."
                                )

                            refresh_page()

                        except Exception as exc:

                            show_error(
                                "Could not save answer.",
                                exc,
                            )


            # --------------------------------------
            # FOLLOW-UP
            # --------------------------------------

            with button_col2:

                followup_clicked = (
                    st.button(
                        "Generate Follow-up",
                        key=(
                            "followup_"
                            + str(question_id)
                        ),
                        disabled=(
                            not bool(
                                existing_answer
                            )
                        ),
                    )
                )


                if followup_clicked:

                    try:

                        with st.spinner(
                            "Generating follow-up..."
                        ):

                            result = (
                                generate_interview_followup(
                                    interview_id=(
                                        selected_interview_id
                                    ),
                                    question_id=(
                                        question_id
                                    ),
                                )
                            )

                        st.success(
                            "Follow-up question "
                            "generated."
                        )

                        st.write(
                            result.get(
                                "question"
                            )
                        )

                        st.caption(
                            result.get(
                                "reason",
                                "",
                            )
                        )

                        refresh_page()

                    except Exception as exc:

                        show_error(
                            "Could not generate "
                            "follow-up.",
                            exc,
                        )


# ==================================================
# COMPLETE INTERVIEW
# ==================================================

if status == "in_progress":

    st.divider()

    st.subheader(
        "Complete Interview"
    )

    st.warning(
        "All required original questions "
        "must have answers before the "
        "interview can be completed."
    )


    if st.button(
        "Complete Interview",
        type="primary",
    ):

        try:

            result = complete_interview(
                selected_interview_id
            )

            st.success(
                "Interview completed."
            )

            st.write(
                "Status:",
                result.get("status"),
            )

            refresh_page()

        except Exception as exc:

            show_error(
                "Could not complete interview.",
                exc,
            )


# ==================================================
# EVALUATION
# ==================================================

if status == "completed":

    st.divider()

    st.subheader(
        "AI-Assisted Evaluation"
    )


    existing_evaluation = (
        interview_detail.get(
            "evaluation"
        )
    )


    if existing_evaluation:

        st.success(
            "This interview has already "
            "been evaluated."
        )

    else:

        st.info(
            "The interview is complete and "
            "ready for AI-assisted evaluation."
        )


        if st.button(
            "Evaluate Interview",
            type="primary",
        ):

            try:

                with st.spinner(
                    "Evaluating interview..."
                ):

                    result = (
                        evaluate_interview(
                            selected_interview_id
                        )
                    )

                st.success(
                    "Evaluation completed."
                )

                st.write(
                    "Overall Score:",
                    result.get(
                        "overall_score"
                    ),
                )

                st.write(
                    "Recommendation:",
                    result.get(
                        "recommendation"
                    ),
                )

                refresh_page()

            except Exception as exc:

                show_error(
                    "Could not evaluate interview.",
                    exc,
                )


# ==================================================
# DISPLAY EVALUATION
# ==================================================

evaluation = interview_detail.get(
    "evaluation"
)


if evaluation:

    st.divider()

    st.subheader(
        "AI-Assisted Evaluation Result"
    )

    st.caption(
        "Structured evaluation generated from "
        "the candidate's interview responses."
    )


    # ==============================================
    # OVERALL RESULT
    # ==============================================

    overall_col1, overall_col2 = (
        st.columns(2)
    )


    with overall_col1:

        st.metric(
            "Overall Score",
            evaluation.get(
                "overall_score",
                0,
            ),
        )


    with overall_col2:

        st.metric(
            "AI Recommendation",
            evaluation.get(
                "recommendation",
                "N/A",
            ),
        )


    # ==============================================
    # DIMENSION SCORES
    # ==============================================

    st.markdown(
        "### Evaluation Dimensions"
    )


    score_col1, score_col2 = (
        st.columns(2)
    )


    with score_col1:

        st.metric(
            "Technical",
            evaluation.get(
                "technical_score",
                0,
            ),
        )

        st.metric(
            "Problem Solving",
            evaluation.get(
                "problem_solving_score",
                0,
            ),
        )


    with score_col2:

        st.metric(
            "Communication",
            evaluation.get(
                "communication_score",
                0,
            ),
        )

        st.metric(
            "Experience",
            evaluation.get(
                "experience_score",
                0,
            ),
        )


    # ==============================================
    # SCORE TABLE
    # ==============================================

    st.markdown(
        "### Score Breakdown"
    )


    score_data = [
        {
            "Dimension": "Technical",
            "Score": evaluation.get(
                "technical_score",
                0,
            ),
            "Weight": "40%",
        },
        {
            "Dimension": "Problem Solving",
            "Score": evaluation.get(
                "problem_solving_score",
                0,
            ),
            "Weight": "25%",
        },
        {
            "Dimension": "Experience",
            "Score": evaluation.get(
                "experience_score",
                0,
            ),
            "Weight": "20%",
        },
        {
            "Dimension": "Communication",
            "Score": evaluation.get(
                "communication_score",
                0,
            ),
            "Weight": "15%",
        },
    ]


    st.dataframe(
        score_data,
        use_container_width=True,
        hide_index=True,
    )


    # ==============================================
    # STRENGTHS AND CONCERNS
    # ==============================================

    strengths = (
        evaluation.get(
            "strengths",
            [],
        )
        or []
    )


    concerns = (
        evaluation.get(
            "concerns",
            [],
        )
        or []
    )


    result_col1, result_col2 = (
        st.columns(2)
    )


    with result_col1:

        st.markdown(
            "### Strengths"
        )

        if strengths:

            for strength in strengths:

                st.write(
                    "• " + str(strength)
                )

        else:

            st.write(
                "No strengths recorded."
            )


    with result_col2:

        st.markdown(
            "### Concerns"
        )

        if concerns:

            for concern in concerns:

                st.write(
                    "• " + str(concern)
                )

        else:

            st.write(
                "No concerns recorded."
            )


    # ==============================================
    # SUMMARY
    # ==============================================

    st.markdown(
        "### Evaluation Summary"
    )


    summary = evaluation.get(
        "summary"
    )


    if summary:

        st.write(
            summary
        )

    else:

        st.write(
            "No evaluation summary available."
        )


    # ==============================================
    # EVALUATION INFORMATION
    # ==============================================

    evaluation_id = evaluation.get(
        "evaluation_id"
    )

    created_at = evaluation.get(
        "created_at"
    )


    if evaluation_id:

        st.caption(
            "Evaluation ID: "
            + str(evaluation_id)
        )


    if created_at:

        st.caption(
            "Evaluation generated: "
            + str(created_at)
        )


    st.info(
        "AI-generated interview scores and "
        "recommendations are decision-support "
        "information. Final recruitment decisions "
        "remain with the recruiter."
    )