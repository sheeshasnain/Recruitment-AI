from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from frontend.api_client import (
    approve_interview_schedule,
    get_interviews,
    get_schedules,
    propose_interview_schedule,
)


st.set_page_config(
    page_title="Scheduling | Recruitment AI",
    page_icon="📅",
    layout="wide",
)


st.title("📅 Interview Scheduling")

st.caption(
    "Prepare interview schedules, review AI-generated "
    "calendar drafts, and create Google Calendar events "
    "after recruiter approval."
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


def format_datetime(value):
    if not value:
        return "N/A"

    try:
        parsed = datetime.fromisoformat(
            str(value).replace(
                "Z",
                "+00:00",
            )
        )

        return parsed.strftime(
            "%d %b %Y, %I:%M %p"
        )

    except Exception:
        return str(value)


# ==================================================
# LOAD DATA
# ==================================================

try:

    schedules = get_schedules()

except Exception as exc:

    schedules = []

    show_error(
        "Could not load interview schedules.",
        exc,
    )


try:

    interviews = get_interviews()

except Exception as exc:

    interviews = []

    show_error(
        "Could not load interviews.",
        exc,
    )


# ==================================================
# OVERVIEW
# ==================================================

total_schedules = len(
    schedules
)

pending_count = sum(
    1
    for schedule in schedules
    if schedule.get("status")
    == "pending_approval"
)

scheduled_count = sum(
    1
    for schedule in schedules
    if schedule.get("status")
    == "scheduled"
)

rejected_count = sum(
    1
    for schedule in schedules
    if schedule.get("status")
    == "rejected"
)


active_schedule_interview_ids = {
    schedule.get("interview_id")
    for schedule in schedules
    if schedule.get("status")
    in {
        "pending_approval",
        "scheduled",
    }
}


unscheduled_count = sum(
    1
    for interview in interviews
    if interview.get("interview_id")
    not in active_schedule_interview_ids
)


metric1, metric2, metric3, metric4 = (
    st.columns(4)
)


with metric1:

    st.metric(
        "Scheduled",
        scheduled_count,
    )


with metric2:

    st.metric(
        "Pending Approval",
        pending_count,
    )


with metric3:

    st.metric(
        "Unscheduled",
        unscheduled_count,
    )


with metric4:

    st.metric(
        "Rejected",
        rejected_count,
    )


# ==================================================
# PROPOSE NEW SCHEDULE
# ==================================================

st.divider()

st.subheader(
    "Propose Interview Schedule"
)

st.caption(
    "Creating a proposal does not create a "
    "Google Calendar event. Calendar creation "
    "requires separate recruiter approval."
)


available_interviews = [
    interview
    for interview in interviews
    if interview.get("interview_id")
    not in active_schedule_interview_ids
]


if not available_interviews:

    st.info(
        "There are no interviews currently "
        "waiting for a schedule."
    )

else:

    interview_options = {}

    for interview in available_interviews:

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
            interview
        )


    selected_label = st.selectbox(
        "Select Interview",
        options=list(
            interview_options.keys()
        ),
    )


    selected_interview = (
        interview_options[
            selected_label
        ]
    )


    info_col1, info_col2 = (
        st.columns(2)
    )


    with info_col1:

        st.write(
            "**Candidate:**",
            selected_interview.get(
                "candidate_name"
            ),
        )


    with info_col2:

        st.write(
            "**Job:**",
            selected_interview.get(
                "job_title"
            ),
        )


    # ==============================================
    # DATE / TIME
    # ==============================================

    date_col, time_col = (
        st.columns(2)
    )


    with date_col:

        interview_date = (
            st.date_input(
                "Interview Date",
                value=(
                    datetime.now().date()
                    + timedelta(days=1)
                ),
            )
        )


    with time_col:

        start_time = (
            st.time_input(
                "Start Time",
                value=time(
                    hour=10,
                    minute=0,
                ),
            )
        )


    duration = st.selectbox(
        "Interview Duration",
        options=[
            30,
            45,
            60,
            90,
        ],
        index=2,
        format_func=lambda value: (
            str(value)
            + " minutes"
        ),
    )


    timezone_name = st.selectbox(
        "Timezone",
        options=[
            "Asia/Dubai",
            "Asia/Karachi",
            "UTC",
            "Europe/London",
            "Europe/Berlin",
            "America/New_York",
        ],
        index=0,
    )


    # ==============================================
    # PREVIEW TIME
    # ==============================================

    local_start = datetime.combine(
        interview_date,
        start_time,
    )


    local_end = (
        local_start
        + timedelta(
            minutes=duration
        )
    )


    st.write(
        "**Start:**",
        local_start.strftime(
            "%d %b %Y, %I:%M %p"
        ),
    )

    st.write(
        "**End:**",
        local_end.strftime(
            "%d %b %Y, %I:%M %p"
        ),
    )

    st.write(
        "**Timezone:**",
        timezone_name,
    )


    # ==============================================
    # CREATE PROPOSAL
    # ==============================================

    if st.button(
        "Generate Schedule Proposal",
        type="primary",
    ):

        try:

            timezone_info = ZoneInfo(
                timezone_name
            )

            aware_start = (
                local_start.replace(
                    tzinfo=timezone_info
                )
            )

            aware_end = (
                local_end.replace(
                    tzinfo=timezone_info
                )
            )


            with st.spinner(
                "Preparing interview "
                "schedule draft..."
            ):

                result = (
                    propose_interview_schedule(
                        interview_id=(
                            selected_interview.get(
                                "interview_id"
                            )
                        ),
                        scheduled_start=(
                            aware_start.isoformat()
                        ),
                        scheduled_end=(
                            aware_end.isoformat()
                        ),
                        timezone=(
                            timezone_name
                        ),
                    )
                )


            st.success(
                "Schedule proposal created."
            )

            st.write(
                "Schedule ID:",
                result.get(
                    "schedule_id"
                ),
            )

            st.rerun()


        except Exception as exc:

            show_error(
                "Could not create "
                "schedule proposal.",
                exc,
            )


# ==================================================
# SCHEDULE LIST
# ==================================================

st.divider()

st.subheader(
    "Schedule List"
)


if not schedules:

    st.info(
        "No interview schedules "
        "have been created yet."
    )

else:

    schedule_table = []


    for schedule in schedules:

        schedule_table.append(
            {
                "Schedule ID": (
                    schedule.get(
                        "schedule_id"
                    )
                ),
                "Candidate": (
                    schedule.get(
                        "candidate_name"
                    )
                ),
                "Job": (
                    schedule.get(
                        "job_title"
                    )
                ),
                "Start": (
                    format_datetime(
                        schedule.get(
                            "scheduled_start"
                        )
                    )
                ),
                "Timezone": (
                    schedule.get(
                        "timezone"
                    )
                ),
                "Status": (
                    schedule.get(
                        "status"
                    )
                ),
            }
        )


    st.dataframe(
        schedule_table,
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# SCHEDULE WORKSPACE
# ==================================================

if schedules:

    st.divider()

    st.subheader(
        "Schedule Review"
    )


    schedule_options = {}


    for schedule in schedules:

        schedule_id = schedule.get(
            "schedule_id"
        )

        candidate_name = schedule.get(
            "candidate_name",
            "Candidate",
        )

        status = schedule.get(
            "status",
            "unknown",
        )

        label = (
            str(schedule_id)
            + " - "
            + str(candidate_name)
            + " ["
            + str(status)
            + "]"
        )

        schedule_options[label] = (
            schedule
        )


    selected_schedule_label = (
        st.selectbox(
            "Select Schedule",
            options=list(
                schedule_options.keys()
            ),
        )
    )


    selected_schedule = (
        schedule_options[
            selected_schedule_label
        ]
    )


    # ==============================================
    # BASIC DETAILS
    # ==============================================

    detail1, detail2 = (
        st.columns(2)
    )


    with detail1:

        st.write(
            "**Schedule ID:**",
            selected_schedule.get(
                "schedule_id"
            ),
        )

        st.write(
            "**Interview ID:**",
            selected_schedule.get(
                "interview_id"
            ),
        )

        st.write(
            "**Candidate:**",
            selected_schedule.get(
                "candidate_name"
            ),
        )

        st.write(
            "**Candidate Email:**",
            selected_schedule.get(
                "candidate_email"
            ),
        )


    with detail2:

        st.write(
            "**Job:**",
            selected_schedule.get(
                "job_title"
            ),
        )

        st.write(
            "**Status:**",
            selected_schedule.get(
                "status"
            ),
        )

        st.write(
            "**Timezone:**",
            selected_schedule.get(
                "timezone"
            ),
        )

        st.write(
            "**Meeting Type:**",
            selected_schedule.get(
                "meeting_type",
                "google_meet",
            ),
        )


    st.write(
        "**Start:**",
        format_datetime(
            selected_schedule.get(
                "scheduled_start"
            )
        ),
    )

    st.write(
        "**End:**",
        format_datetime(
            selected_schedule.get(
                "scheduled_end"
            )
        ),
    )


    # ==============================================
    # CALENDAR DRAFT
    # ==============================================

    st.markdown(
        "### Calendar Event Draft"
    )


    st.write(
        "**Title:**"
    )

    st.write(
        selected_schedule.get(
            "event_title"
        )
        or "No title generated."
    )


    st.write(
        "**Description:**"
    )

    st.write(
        selected_schedule.get(
            "event_description"
        )
        or "No description generated."
    )


    st.markdown(
        "### Candidate Message"
    )

    st.write(
        selected_schedule.get(
            "candidate_message"
        )
        or "No candidate message generated."
    )


    schedule_status = (
        selected_schedule.get(
            "status"
        )
    )


    # ==============================================
    # RECRUITER APPROVAL
    # ==============================================

    if (
        schedule_status
        == "pending_approval"
    ):

        st.warning(
            "This schedule is awaiting recruiter "
            "approval. Approving it will create a "
            "real Google Calendar event and invite "
            "the candidate."
        )


        reject_col, approve_col = (
            st.columns(2)
        )


        with reject_col:

            if st.button(
                "Reject Proposal",
                use_container_width=True,
            ):

                try:

                    result = (
                        approve_interview_schedule(
                            schedule_id=(
                                selected_schedule.get(
                                    "schedule_id"
                                )
                            ),
                            approved=False,
                        )
                    )

                    st.success(
                        "Schedule proposal rejected."
                    )

                    st.rerun()

                except Exception as exc:

                    show_error(
                        "Could not reject "
                        "schedule proposal.",
                        exc,
                    )


        with approve_col:

            if st.button(
                "Approve & Create Calendar Event",
                type="primary",
                use_container_width=True,
            ):

                try:

                    with st.spinner(
                        "Creating Google Calendar "
                        "event..."
                    ):

                        result = (
                            approve_interview_schedule(
                                schedule_id=(
                                    selected_schedule.get(
                                        "schedule_id"
                                    )
                                ),
                                approved=True,
                            )
                        )


                    st.success(
                        "Interview scheduled "
                        "successfully."
                    )

                    st.rerun()


                except Exception as exc:

                    show_error(
                        "Google Calendar event "
                        "could not be created.",
                        exc,
                    )


    # ==============================================
    # SCHEDULED
    # ==============================================

    elif schedule_status == "scheduled":

        st.success(
            "Google Calendar event created."
        )


        google_event_id = (
            selected_schedule.get(
                "google_event_id"
            )
        )


        meeting_link = (
            selected_schedule.get(
                "meeting_link"
            )
        )


        if google_event_id:

            st.write(
                "**Google Event ID:**",
                google_event_id,
            )


        if meeting_link:

            st.link_button(
                "Open Google Meet",
                meeting_link,
                type="primary",
            )

        else:

            st.info(
                "No Google Meet link "
                "was returned."
            )


    # ==============================================
    # REJECTED
    # ==============================================

    elif schedule_status == "rejected":

        st.warning(
            "This schedule proposal was rejected. "
            "The interview is available again in "
            "'Propose Interview Schedule' so you "
            "can choose a new date or time."
        )