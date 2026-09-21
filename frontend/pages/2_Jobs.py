import streamlit as st

from frontend.api_client import (
    create_job,
    get_jobs,
)


st.set_page_config(
    page_title="Jobs | Recruitment AI",
    page_icon="💼",
    layout="wide",
)


st.title("💼 Jobs")

st.caption(
    "Create and manage job openings used by "
    "the AI recruitment workflow."
)


# ==================================================
# CREATE JOB
# ==================================================

st.subheader("Create New Job")


with st.form(
    "create_job_form",
    clear_on_submit=True,
):

    title = st.text_input(
        "Job Title",
        placeholder="e.g. Senior Python Developer",
    )

    description = st.text_area(
        "Job Description",
        placeholder=(
            "Describe the role, responsibilities, "
            "requirements, and expectations..."
        ),
        height=180,
    )

    skills_text = st.text_input(
        "Required Skills",
        placeholder=(
            "Python, FastAPI, PostgreSQL, Docker"
        ),
        help=(
            "Enter skills separated by commas."
        ),
    )

    minimum_experience = st.number_input(
        "Minimum Experience (Years)",
        min_value=0.0,
        max_value=50.0,
        value=0.0,
        step=0.5,
    )

    submitted = st.form_submit_button(
        "Create Job",
        type="primary",
    )


# ==================================================
# HANDLE JOB CREATION
# ==================================================

if submitted:

    clean_title = title.strip()
    clean_description = description.strip()

    required_skills = [
        skill.strip()
        for skill in skills_text.split(",")
        if skill.strip()
    ]

    if not clean_title:

        st.error(
            "Job title is required."
        )

    elif not clean_description:

        st.error(
            "Job description is required."
        )

    elif not required_skills:

        st.error(
            "Please enter at least one "
            "required skill."
        )

    else:

        try:

            with st.spinner(
                "Creating job..."
            ):

                created_job = create_job(
                    title=clean_title,
                    description=clean_description,
                    required_skills=required_skills,
                    minimum_experience=(
                        float(
                            minimum_experience
                        )
                    ),
                )

            st.success(
                "Job created successfully."
            )

            st.write(
                f"Job ID: "
                f"{created_job.get('id')}"
            )

        except Exception as exc:

            st.error(
                "Could not create the job."
            )

            st.exception(exc)


# ==================================================
# JOB LIST
# ==================================================

st.divider()

st.subheader("Existing Jobs")


try:

    with st.spinner(
        "Loading jobs..."
    ):

        jobs = get_jobs()


    if not jobs:

        st.info(
            "No jobs have been created yet."
        )

    else:

        # ------------------------------------------
        # Summary metrics
        # ------------------------------------------

        total_jobs = len(jobs)

        active_jobs = sum(
            1
            for job in jobs
            if job.get("is_active", True)
        )

        inactive_jobs = (
            total_jobs - active_jobs
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Total Jobs",
                total_jobs,
            )


        with col2:

            st.metric(
                "Active Jobs",
                active_jobs,
            )


        with col3:

            st.metric(
                "Inactive Jobs",
                inactive_jobs,
            )


        st.divider()


        # ------------------------------------------
        # Job table
        # ------------------------------------------

        table_data = []

        for job in jobs:

            skills = job.get(
                "required_skills",
                [],
            ) or []

            table_data.append(
                {
                    "ID": job.get("id"),
                    "Title": job.get("title"),
                    "Required Skills": (
                        ", ".join(skills)
                    ),
                    "Minimum Experience": (
                        job.get(
                            "minimum_experience",
                            0,
                        )
                    ),
                    "Active": job.get(
                        "is_active",
                        True,
                    ),
                    "Created At": job.get(
                        "created_at"
                    ),
                }
            )


        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True,
        )


        # ------------------------------------------
        # Detailed job viewer
        # ------------------------------------------

        st.subheader(
            "Job Details"
        )


        job_options = {
            (
                f"{job.get('id')} - "
                f"{job.get('title')}"
            ): job
            for job in jobs
        }


        selected_label = st.selectbox(
            "Select a job",
            options=list(
                job_options.keys()
            ),
        )


        selected_job = (
            job_options[
                selected_label
            ]
        )


        st.markdown(
            f"### "
            f"{selected_job.get('title')}"
        )


        detail_col1, detail_col2 = (
            st.columns(2)
        )


        with detail_col1:

            st.write(
                "**Job ID:**",
                selected_job.get("id"),
            )

            minimum_exp = selected_job.get(
                "minimum_experience",
                0,
            )

            st.write(
                "**Minimum Experience:**",
                f"{'minimum_experience',} years",
            )


        with detail_col2:

            st.write(
                "**Active:**",
                selected_job.get(
                    "is_active",
                    True,
                ),
            )

            st.write(
                "**Created:**",
                selected_job.get(
                    "created_at",
                    "N/A",
                ),
            )


        st.write(
            "**Required Skills:**"
        )


        selected_skills = (
            selected_job.get(
                "required_skills",
                [],
            )
            or []
        )


        if selected_skills:

            st.write(
                ", ".join(
                    selected_skills
                )
            )

        else:

            st.write(
                "No skills specified."
            )


        st.write(
            "**Job Description:**"
        )

        st.write(
            selected_job.get(
                "description",
                "",
            )
        )


except Exception as exc:

    st.error(
        "Could not load jobs from the backend."
    )

    st.exception(exc)