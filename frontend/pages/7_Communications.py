import streamlit as st

from frontend.api_client import (
    approve_communication,
    create_communication_draft,
    get_applications,
    get_communications,
    update_communication_draft,
)

st.set_page_config(
    page_title=(
        "Communications | Recruitment AI"
    ),
    page_icon="✉️",
    layout="wide",
)


st.title(
    "✉️ Candidate Communications"
)

st.caption(
    "Generate candidate email drafts, review them, "
    "and send approved communications through Gmail."
)


# ==================================================
# HELPERS
# ==================================================


def show_error(
    message,
    exc,
):

    st.error(
        message
    )

    try:

        st.json(
            exc.response.json()
        )

    except Exception:

        st.exception(
            exc
        )


def format_communication_type(
    value,
):

    mapping = {
        "interview_invitation":
            "Interview Invitation",
        "interview_reminder":
            "Interview Reminder",
        "follow_up":
            "Follow Up",
    }

    return mapping.get(
        value,
        str(value)
        .replace("_", " ")
        .title(),
    )


# ==================================================
# LOAD DATA
# ==================================================

try:

    communications = (
        get_communications()
    )

except Exception as exc:

    communications = []

    show_error(
        "Could not load communications.",
        exc,
    )


try:

    applications = (
        get_applications()
    )

except Exception as exc:

    applications = []

    show_error(
        "Could not load applications.",
        exc,
    )


# ==================================================
# METRICS
# ==================================================

total_count = len(
    communications
)

draft_count = sum(
    1
    for item in communications
    if item.get("status")
    == "draft"
)

sent_count = sum(
    1
    for item in communications
    if item.get("status")
    == "sent"
)

rejected_count = sum(
    1
    for item in communications
    if item.get("status")
    == "rejected"
)


metric1, metric2, metric3, metric4 = (
    st.columns(4)
)


with metric1:

    st.metric(
        "Total",
        total_count,
    )


with metric2:

    st.metric(
        "Awaiting Approval",
        draft_count,
    )


with metric3:

    st.metric(
        "Sent",
        sent_count,
    )


with metric4:

    st.metric(
        "Rejected",
        rejected_count,
    )


# ==================================================
# CREATE EMAIL DRAFT
# ==================================================

st.divider()

st.subheader(
    "Create Communication Draft"
)

st.caption(
    "Generating a draft does not send an email. "
    "Gmail is called only after recruiter approval."
)


if not applications:

    st.info(
        "No applications are available."
    )

else:

    application_options = {}


    for application in applications:

        application_id = (
            application.get("id")
            or application.get(
                "application_id"
            )
        )

        candidate_name = (
            application.get(
                "candidate_name"
            )
            or "Candidate"
        )

        job_title = (
            application.get(
                "job_title"
            )
            or "Job"
        )

        status = (
            application.get(
                "status"
            )
            or "unknown"
        )

        label = (
            str(application_id)
            + " - "
            + str(candidate_name)
            + " - "
            + str(job_title)
            + " ["
            + str(status)
            + "]"
        )

        application_options[
            label
        ] = application


    selected_application_label = (
        st.selectbox(
            "Select Application",
            options=list(
                application_options.keys()
            ),
        )
    )


    selected_application = (
        application_options[
            selected_application_label
        ]
    )


    application_id = (
        selected_application.get(
            "id"
        )
        or selected_application.get(
            "application_id"
        )
    )


    info1, info2, info3 = (
        st.columns(3)
    )


    with info1:

        st.write(
            "**Candidate:**",
            selected_application.get(
                "candidate_name",
                "Unknown",
            ),
        )


    with info2:

        st.write(
            "**Job:**",
            selected_application.get(
                "job_title",
                "Unknown",
            ),
        )


    with info3:

        st.write(
            "**Application Status:**",
            selected_application.get(
                "status",
                "Unknown",
            ),
        )


    communication_type = (
        st.selectbox(
            "Communication Type",
            options=[
                "interview_invitation",
                "interview_reminder",
                "follow_up",
            ],
            format_func=(
                format_communication_type
            ),
        )
    )


    # ==============================================
    # COMMUNICATION TYPE INFORMATION
    # ==============================================

    if (
        communication_type
        == "interview_invitation"
    ):

        st.info(
            "Interview Invitation requires a "
            "scheduled interview. The email can "
            "include the interview date, timezone "
            "and meeting link."
        )

    elif (
        communication_type
        == "interview_reminder"
    ):

        st.info(
            "Interview Reminder requires a "
            "scheduled interview."
        )

    else:

        st.info(
            "Follow Up can be generated without "
            "an interview schedule."
        )


    if st.button(
        "Generate Email Draft",
        type="primary",
    ):

        try:

            with st.spinner(
                "Generating candidate "
                "email draft..."
            ):

                result = (
                    create_communication_draft(
                        application_id=(
                            application_id
                        ),
                        communication_type=(
                            communication_type
                        ),
                    )
                )


            st.success(
                "Email draft created."
            )

            st.write(
                "**Communication ID:**",
                result.get(
                    "communication_id"
                ),
            )

            st.rerun()


        except Exception as exc:

            show_error(
                "Could not generate "
                "communication draft.",
                exc,
            )


# ==================================================
# COMMUNICATION HISTORY
# ==================================================

st.divider()

st.subheader(
    "Communication History"
)


if not communications:

    st.info(
        "No candidate communications "
        "have been created yet."
    )

else:

    history = []


    for item in communications:

        history.append(
            {
                "ID": (
                    item.get(
                        "communication_id"
                    )
                ),
                "Candidate": (
                    item.get(
                        "candidate_name"
                    )
                ),
                "Job": (
                    item.get(
                        "job_title"
                    )
                ),
                "Type": (
                    format_communication_type(
                        item.get(
                            "communication_type"
                        )
                    )
                ),
                "Recipient": (
                    item.get(
                        "recipient"
                    )
                ),
                "Status": (
                    item.get(
                        "status"
                    )
                ),
                "Sent At": (
                    item.get(
                        "sent_at"
                    )
                    or "-"
                ),
            }
        )


    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# COMMUNICATION REVIEW
# ==================================================

if communications:

    st.divider()

    st.subheader(
        "Communication Review"
    )


    communication_options = {}


    for item in communications:

        communication_id = (
            item.get(
                "communication_id"
            )
        )

        candidate_name = (
            item.get(
                "candidate_name",
                "Candidate",
            )
        )

        communication_type = (
            format_communication_type(
                item.get(
                    "communication_type"
                )
            )
        )

        status = (
            item.get(
                "status",
                "unknown",
            )
        )

        label = (
            str(communication_id)
            + " - "
            + str(candidate_name)
            + " - "
            + str(communication_type)
            + " ["
            + str(status)
            + "]"
        )

        communication_options[
            label
        ] = item


    selected_label = (
        st.selectbox(
            "Select Communication",
            options=list(
                communication_options.keys()
            ),
        )
    )


    selected_communication = (
        communication_options[
            selected_label
        ]
    )


    # ==============================================
    # DETAILS
    # ==============================================

    detail1, detail2 = (
        st.columns(2)
    )


    with detail1:

        st.write(
            "**Candidate:**",
            selected_communication.get(
                "candidate_name"
            ),
        )

        st.write(
            "**Recipient:**",
            selected_communication.get(
                "recipient"
            ),
        )

        st.write(
            "**Application ID:**",
            selected_communication.get(
                "application_id"
            ),
        )


    with detail2:

        st.write(
            "**Job:**",
            selected_communication.get(
                "job_title"
            ),
        )

        st.write(
            "**Type:**",
            format_communication_type(
                selected_communication.get(
                    "communication_type"
                )
            ),
        )

        st.write(
            "**Status:**",
            selected_communication.get(
                "status"
            ),
        )


    # ==============================================
    # EMAIL EDITOR / PREVIEW
    # ==============================================

    st.markdown(
        "### Email Review"
    )


    communication_status = (
        selected_communication.get(
            "status"
        )
    )


    is_editable = (
        communication_status
        == "draft"
    )


    if is_editable:

        st.info(
            "This draft was generated by the "
            "Communication Agent. Review and edit "
           "it before approving delivery."
        )


    edited_subject = st.text_input(
        "Subject",
        value=(
            selected_communication.get(
                "subject"
            )
            or ""
        ),
        disabled=not is_editable,
        key=(
            "communication_subject_"
            + str(
                selected_communication.get(
                    "communication_id"
                )
            )
        ),
    )


    edited_body = st.text_area(
        "Email Body",
        value=(
            selected_communication.get(
                "body"
            )
            or ""
        ),
        height=320,
        disabled=not is_editable,
        key=(
            "communication_body_"
            + str(
                selected_communication.get(
                    "communication_id"
                )
            )
        ),
    )


    if is_editable:

        original_subject = (
            selected_communication.get(
                "subject"
            )
            or ""
        )

        original_body = (
            selected_communication.get(
                "body"
            )
            or ""
        )


        has_changes = (
            edited_subject.strip()
            != original_subject.strip()
            or
            edited_body.strip()
            != original_body.strip()
        )


        if has_changes:

            st.warning(
                "You have unsaved changes."
            )

        else:

            st.caption(
                "No unsaved changes."
            )


        if st.button(
            "Save Draft Changes",
            disabled=not has_changes,
            use_container_width=True,
        ):

            if len(
                edited_subject.strip()
            ) < 3:

                st.error(
                    "Subject must contain at "
                    "least 3 characters."
                )

            elif len(
                edited_body.strip()
            ) < 10:

                st.error(
                    "Email body must contain at "
                    "least 10 characters."
                )

            else:

                try:

                    update_communication_draft(
                        communication_id=(
                            selected_communication.get(
                                "communication_id"
                            )
                        ),
                        subject=(
                            edited_subject.strip()
                        ),
                        body=(
                            edited_body.strip()
                        ),
                    )

                    st.success(
                        "Draft changes saved."
                    )

                    st.rerun()

                except Exception as exc:

                    show_error(
                        "Could not save "
                        "draft changes.",
                        exc,
                    )


    # ==============================================
    # HUMAN APPROVAL
    # ==============================================

    if communication_status == "draft":

        st.warning(
            "This email is awaiting recruiter "
            "approval. Approving it will send a "
            "real email to the candidate using Gmail."
        )


        reject_col, approve_col = (
            st.columns(2)
        )


        with reject_col:

            if st.button(
                "Reject Email",
                use_container_width=True,
            ):

                try:

                    approve_communication(
                        communication_id=(
                            selected_communication.get(
                                "communication_id"
                            )
                        ),
                        approved=False,
                    )

                    st.success(
                        "Email draft rejected."
                    )

                    st.rerun()


                except Exception as exc:

                    show_error(
                        "Could not reject "
                        "email draft.",
                        exc,
                    )


        with approve_col:

            if st.button(
                "Approve & Send Email",
                type="primary",
                use_container_width=True,
                disabled=has_changes,
            ):

                try:

                    with st.spinner(
                        "Sending email "
                        "through Gmail..."
                    ):

                        result = (
                            approve_communication(
                                communication_id=(
                                    selected_communication.get(
                                        "communication_id"
                                    )
                                ),
                                approved=True,
                            )
                        )


                    st.success(
                        "Email sent successfully."
                    )

                    st.rerun()


                except Exception as exc:

                    show_error(
                        "Email could not be sent.",
                        exc,
                    )

        if has_changes:
            st.caption(
                "Save your draft changes before "
                "approving and sending the email."
            )

    # ==============================================
    # SENT
    # ==============================================

    elif communication_status == "sent":

        st.success(
            "This email was sent successfully."
        )

        st.caption(
            "Sent communications are locked "
            "and can no longer be edited."
        )


        provider_message_id = (
            selected_communication.get(
                "provider_message_id"
            )
        )


        if provider_message_id:

            st.write(
                "**Gmail Message ID:**",
                provider_message_id,
            )


        if selected_communication.get(
            "sent_at"
        ):

            st.write(
                "**Sent At:**",
                selected_communication.get(
                    "sent_at"
                ),
            )


    # ==============================================
    # REJECTED
    # ==============================================

    elif communication_status == "rejected":

        st.warning(
            "This email draft was rejected "
            "by the recruiter. No email was sent."
        )

        st.caption(
            "Rejected communications are locked. "
            "Create a new draft if another email "
            "is required."
        )