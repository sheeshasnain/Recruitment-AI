import streamlit as st
import httpx


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Recruitment AI",
    page_icon="🤖",
    layout="wide",
)


st.title("Recruitment AI")
st.caption(
    "AI-powered recruitment and interview operations platform"
)


st.subheader("Groq Connection Test")

prompt = st.text_area(
    "Ask the recruitment assistant something:",
    placeholder="Generate interview questions for a Python developer...",
)


if st.button("Send"):
    if not prompt.strip():
        st.warning("Please enter a message.")

    else:
        try:
            with st.spinner("Thinking..."):
                response = httpx.post(
                    f"{API_BASE_URL}/api/v1/llm/test",
                    json={
                        "message": prompt
                    },
                    timeout=60,
                )

            response.raise_for_status()

            result = response.json()

            st.success("Response received")
            st.write(result["response"])

        except Exception as exc:
            st.error(
                "Could not communicate with the backend."
            )