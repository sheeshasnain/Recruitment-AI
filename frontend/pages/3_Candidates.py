import streamlit as st

from frontend.api_client import (
    create_candidate,
    get_candidates,
)


st.set_page_config(
    page_title="Candidates | Recruitment AI",
    page_icon="👤",
    layout="wide",
)


st.title("👤 Candidates")

st.caption(
    "Add candidates, upload resumes, and review "
    "candidate profiles."
)


# ==================================================
# CREATE CANDIDATE
# ==================================================

st.subheader("Add New Candidate")

with st.form(
    "create_candidate_form",
    clear_on_submit=False,
):

    name = st.text_input(
        "Candidate Name",
        placeholder="e.g. John Smith",
    )

    email = st.text_input(
        "Email Address",
        placeholder="candidate@example.com",
    )

    phone = st.text_input(
        "Phone Number",
        placeholder="+971 50 123 4567",
    )

    resume = st.file_uploader(
        "Upload Resume",
        type=[
            "pdf",
            "docx",
            "txt",
        ],
        help=(
            "Supported formats: PDF, DOCX and TXT."
        ),
    )

    submitted = st.form_submit_button(
        "Add Candidate",
        type="primary",
    )


# ==================================================
# HANDLE CANDIDATE CREATION
# ==================================================

if submitted:

    clean_name = name.strip()
    clean_email = email.strip().lower()
    clean_phone = phone.strip()

    if not clean_name:

        st.error(
            "Candidate name is required."
        )

    elif not clean_email:

        st.error(
            "Candidate email is required."
        )

    elif resume is None:

        st.error(
            "Please upload a candidate resume."
        )

    else:

        try:

            with st.spinner(
                "Uploading and processing resume..."
            ):

                created_candidate = create_candidate(
                    name=clean_name,
                    email=clean_email,
                    phone=(
                        clean_phone
                        if clean_phone
                        else None
                    ),
                    resume_name=resume.name,
                    resume_bytes=resume.getvalue(),
                    resume_content_type=(
                        resume.type
                        or "application/octet-stream"
                    ),
                )

            st.success(
                "Candidate created successfully."
            )

            st.write(
                "Candidate ID:",
                created_candidate.get("id"),
            )

            st.write(
                "Resume:",
                created_candidate.get(
                    "resume_filename"
                ),
            )

        except Exception as exc:

            st.error(
                "Could not create candidate."
            )

            st.exception(exc)


# ==================================================
# EXISTING CANDIDATES
# ==================================================

st.divider()

st.subheader("Existing Candidates")


try:

    with st.spinner(
        "Loading candidates..."
    ):

        candidates = get_candidates()


    if not candidates:

        st.info(
            "No candidates have been added yet."
        )

    else:

        # ==========================================
        # SUMMARY METRICS
        # ==========================================

        total_candidates = len(
            candidates
        )

        candidates_with_role = sum(
            1
            for candidate in candidates
            if candidate.get("current_role")
        )

        candidates_with_skills = sum(
            1
            for candidate in candidates
            if candidate.get("skills")
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Total Candidates",
                total_candidates,
            )


        with col2:

            st.metric(
                "Profiles Enriched",
                candidates_with_role,
            )


        with col3:

            st.metric(
                "Skills Identified",
                candidates_with_skills,
            )


        st.divider()


        # ==========================================
        # CANDIDATE TABLE
        # ==========================================

        table_data = []

        for candidate in candidates:

            skills = (
                candidate.get(
                    "skills",
                    [],
                )
                or []
            )

            table_data.append(
                {
                    "ID": candidate.get("id"),
                    "Name": candidate.get("name"),
                    "Email": candidate.get("email"),
                    "Current Role": (
                        candidate.get(
                            "current_role"
                        )
                        or "Not extracted"
                    ),
                    "Experience": (
                        candidate.get(
                            "years_experience",
                            0,
                        )
                    ),
                    "Skills": ", ".join(
                        skills
                    ),
                    "Resume": (
                        candidate.get(
                            "resume_filename"
                        )
                        or "N/A"
                    ),
                }
            )


        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True,
        )


        # ==========================================
        # CANDIDATE DETAILS
        # ==========================================

        st.subheader(
            "Candidate Details"
        )


        candidate_options = {
            (
                str(candidate.get("id"))
                + " - "
                + str(candidate.get("name"))
            ): candidate
            for candidate in candidates
        }


        selected_label = st.selectbox(
            "Select a candidate",
            options=list(
                candidate_options.keys()
            ),
        )


        selected_candidate = (
            candidate_options[
                selected_label
            ]
        )


        st.markdown(
            "### "
            + str(
                selected_candidate.get(
                    "name",
                    "Candidate",
                )
            )
        )

        # ==========================================
        # PROFILE ANALYSIS STATUS
        # ==========================================

        profile_analyzed = bool(
            selected_candidate.get("current_role")
            or selected_candidate.get("skills")
            or selected_candidate.get(
                "experience_summary"
            )
        )


        if profile_analyzed:

            st.success(
                "AI profile analysis completed."
            )

        else:

            st.info(
                "Profile analysis pending. "
                "Candidate profile will be extracted "
                "during AI screening."
            )


        # ==========================================
        # BASIC PROFILE
        # ==========================================

        detail_col1, detail_col2 = (
            st.columns(2)
        )


        with detail_col1:

            st.write(
                "**Candidate ID:**",
                selected_candidate.get(
                    "id"
                ),
            )

            st.write(
                "**Email:**",
                selected_candidate.get(
                    "email"
                ),
            )

            st.write(
                "**Phone:**",
                (
                    selected_candidate.get(
                        "phone"
                    )
                    or "Not provided"
                ),
            )


        with detail_col2:

            st.write(
                "**Current Role:**",
                (
                    selected_candidate.get(
                        "current_role"
                    )
                    or "Pending AI screening"
                ),
            )

            experience = selected_candidate.get(
                    "years_experience",
                    0,
            )

            if profile_analyzed:
                experience_display = (
                    str(experience)
                    + "years"
                )

            else:
                experience_display = (
                    "Pending AI screening"
                )


            st.write(
                "**Experience:**",
                experience_display,
            )

            st.write(
                "**Resume:**",
                (
                    selected_candidate.get(
                        "resume_filename"
                    )
                    or "N/A"
                ),
            )


        # ==========================================
        # SKILLS
        # ==========================================

        st.write(
            "**Skills:**"
        )

        selected_skills = (
            selected_candidate.get(
                "skills",
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
                 "Pending AI screening."
            )


        # ==========================================
        # EDUCATION
        # ==========================================

        st.write(
            "**Education:**"
        )

        education = (
            selected_candidate.get(
                "education",
                [],
            )
            or []
        )

        if education:

            for item in education:

                st.write(
                    "• " + str(item)
                )

        else:

            st.write(
                 "Pending AI screening."
            )


        # ==========================================
        # EXPERIENCE SUMMARY
        # ==========================================

        st.write(
            "**Experience Summary:**"
        )

        experience_summary = (
            selected_candidate.get(
                "experience_summary"
            )
        )

        if experience_summary:

            st.write(
                experience_summary
            )

        else:

            st.write(
                 "Pending AI screening."
            )


        # ==========================================
        # CREATED DATE
        # ==========================================

        st.write(
            "**Added:**",
            selected_candidate.get(
                "created_at",
                "N/A",
            ),
        )


except Exception as exc:

    st.error(
        "Could not load candidates "
        "from the backend."
    )

    st.exception(exc)