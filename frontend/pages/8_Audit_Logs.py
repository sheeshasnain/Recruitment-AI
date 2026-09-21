import json

import streamlit as st

from frontend.api_client import (
    get_tool_logs,
)


st.set_page_config(
    page_title="Audit Logs | Recruitment AI",
    page_icon="🔎",
    layout="wide",
)


st.title("🔎 Audit Logs & Observability")

st.caption(
    "Review external tool actions performed by "
    "the recruitment system."
)


# ==================================================
# HELPERS
# ==================================================


def format_payload(payload):
    if payload is None:
        return "No payload recorded."

    try:
        return json.dumps(
            payload,
            indent=2,
            default=str,
        )

    except Exception:
        return str(payload)


def show_error(
    message,
    exc,
):
    st.error(message)

    try:
        st.json(
            exc.response.json()
        )

    except Exception:
        st.exception(exc)


# ==================================================
# OBSERVABILITY ARCHITECTURE
# ==================================================

with st.expander(
    "Observability Architecture",
    expanded=False,
):

    st.markdown(
        """
### LangSmith
Tracks LLM and agent execution traces.

Examples:
- screening agent
- interview preparation agent
- follow-up generation
- interview evaluation
- scheduling agent
- communication agent

### Application Logs
Tracks backend workflow execution and errors.

Examples:
- API requests
- scheduling workflow
- validation failures
- database failures
- application state changes

### Tool Action Logs
Tracks external side effects.

Examples:
- Google Calendar event creation
- Gmail email delivery

External tools are executed only after the
appropriate recruiter approval.
"""
    )


# ==================================================
# LOAD LOGS
# ==================================================

try:
    logs = get_tool_logs()

except Exception as exc:
    logs = []

    show_error(
        "Could not load audit logs.",
        exc,
    )


# ==================================================
# METRICS
# ==================================================

total_count = len(logs)

success_count = sum(
    1
    for log in logs
    if log.get("status") == "success"
)

failed_count = sum(
    1
    for log in logs
    if log.get("status") == "failed"
)

calendar_count = sum(
    1
    for log in logs
    if log.get("tool") == "google_calendar"
)

gmail_count = sum(
    1
    for log in logs
    if log.get("tool") == "gmail"
)


metric1, metric2, metric3, metric4, metric5 = (
    st.columns(5)
)


with metric1:
    st.metric(
        "Total Actions",
        total_count,
    )


with metric2:
    st.metric(
        "Successful",
        success_count,
    )


with metric3:
    st.metric(
        "Failed",
        failed_count,
    )


with metric4:
    st.metric(
        "Calendar",
        calendar_count,
    )


with metric5:
    st.metric(
        "Gmail",
        gmail_count,
    )


# ==================================================
# EMPTY STATE
# ==================================================

if not logs:

    st.info(
        "No external tool actions have "
        "been recorded yet."
    )

    st.stop()


# ==================================================
# FILTERS
# ==================================================

st.divider()

st.subheader("Filters")


tool_values = sorted(
    {
        str(log.get("tool"))
        for log in logs
        if log.get("tool")
    }
)


status_values = sorted(
    {
        str(log.get("status"))
        for log in logs
        if log.get("status")
    }
)


action_values = sorted(
    {
        str(log.get("action"))
        for log in logs
        if log.get("action")
    }
)


filter1, filter2, filter3 = (
    st.columns(3)
)


with filter1:

    selected_tool = st.selectbox(
        "Tool",
        options=[
            "All",
            *tool_values,
        ],
    )


with filter2:

    selected_status = st.selectbox(
        "Status",
        options=[
            "All",
            *status_values,
        ],
    )


with filter3:

    selected_action = st.selectbox(
        "Action",
        options=[
            "All",
            *action_values,
        ],
    )


filtered_logs = logs


if selected_tool != "All":

    filtered_logs = [
        log
        for log in filtered_logs
        if log.get("tool")
        == selected_tool
    ]


if selected_status != "All":

    filtered_logs = [
        log
        for log in filtered_logs
        if log.get("status")
        == selected_status
    ]


if selected_action != "All":

    filtered_logs = [
        log
        for log in filtered_logs
        if log.get("action")
        == selected_action
    ]


st.caption(
    f"Showing {len(filtered_logs)} "
    f"of {len(logs)} audit records."
)


# ==================================================
# AUDIT TABLE
# ==================================================

st.divider()

st.subheader("External Tool Activity")


if not filtered_logs:

    st.info(
        "No audit records match "
        "the selected filters."
    )

else:

    table_rows = []

    for log in filtered_logs:

        table_rows.append(
            {
                "ID": log.get("id"),
                "Tool": log.get("tool"),
                "Action": log.get("action"),
                "Status": log.get("status"),
                "Entity Type": (
                    log.get("entity_type")
                    or "-"
                ),
                "Entity ID": (
                    log.get("entity_id")
                    if log.get("entity_id")
                    is not None
                    else "-"
                ),
                "Created At": (
                    log.get("created_at")
                    or "-"
                ),
            }
        )


    st.dataframe(
        table_rows,
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# AUDIT RECORD INSPECTOR
# ==================================================

if filtered_logs:

    st.divider()

    st.subheader("Audit Record Inspector")


    log_options = {}

    for log in filtered_logs:

        log_id = log.get("id")

        tool_name = (
            log.get("tool")
            or "unknown"
        )

        action = (
            log.get("action")
            or "unknown"
        )

        status = (
            log.get("status")
            or "unknown"
        )

        label = (
            str(log_id)
            + " - "
            + str(tool_name)
            + " / "
            + str(action)
            + " ["
            + str(status)
            + "]"
        )

        log_options[label] = log


    selected_log_label = (
        st.selectbox(
            "Select Audit Record",
            options=list(
                log_options.keys()
            ),
        )
    )


    selected_log = (
        log_options[
            selected_log_label
        ]
    )


    detail1, detail2 = st.columns(2)


    with detail1:

        st.write(
            "**Log ID:**",
            selected_log.get("id"),
        )

        st.write(
            "**Tool:**",
            selected_log.get("tool"),
        )

        st.write(
            "**Action:**",
            selected_log.get("action"),
        )

        st.write(
            "**Status:**",
            selected_log.get("status"),
        )


    with detail2:

        st.write(
            "**Entity Type:**",
            selected_log.get(
                "entity_type"
            )
            or "-",
        )

        st.write(
            "**Entity ID:**",
            selected_log.get(
                "entity_id"
            )
            if selected_log.get(
                "entity_id"
            ) is not None
            else "-",
        )

        st.write(
            "**Created At:**",
            selected_log.get(
                "created_at"
            )
            or "-",
        )


    # ==============================================
    # SUCCESS / FAILURE STATE
    # ==============================================

    if (
        selected_log.get("status")
        == "success"
    ):

        st.success(
            "External tool action "
            "completed successfully."
        )


    elif (
        selected_log.get("status")
        == "failed"
    ):

        st.error(
            "External tool action failed."
        )


    # ==============================================
    # REQUEST
    # ==============================================

    st.markdown(
        "### Request Payload"
    )

    st.code(
        format_payload(
            selected_log.get(
                "request_payload"
            )
        ),
        language="json",
    )


    # ==============================================
    # RESPONSE
    # ==============================================

    st.markdown(
        "### Response Payload"
    )

    st.code(
        format_payload(
            selected_log.get(
                "response_payload"
            )
        ),
        language="json",
    )


    # ==============================================
    # ERROR
    # ==============================================

    error_message = (
        selected_log.get("error")
    )


    if error_message:

        st.markdown(
            "### Error"
        )

        st.error(
            error_message
        )


# ==================================================
# SECURITY NOTE
# ==================================================

st.divider()

st.caption(
    "Audit records should contain operational "
    "metadata only. OAuth tokens, API keys, "
    "credentials and other secrets must never "
    "be stored in ToolActionLog."
)