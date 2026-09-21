import streamlit as st


st.set_page_config(
    page_title="Recruitment AI",
    page_icon="👨‍💻",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("Recruitment AI")

st.caption(
    "AI-powered recruitment and interview "
    "operations platform"
)


st.markdown(
    """
    ### Recruitment Operations Dashboard

    Use the navigation menu to manage the complete
    recruitment workflow.

    **Available operations:**

    - Manage jobs
    - Review candidates
    - Monitor applications
    - Conduct structured interviews
    - Schedule interviews
    - Manage candidate communications
    - Review AI recommendations
    - Make final recruiter decisions
    - Review audit and tool activity
    """
)


st.info(
    "AI provides recommendations and automation, "
    "while final recruitment decisions remain "
    "under recruiter control."
)