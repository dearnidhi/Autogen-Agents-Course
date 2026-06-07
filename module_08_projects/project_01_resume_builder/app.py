"""Simple web UI for the Resume Builder. Run: streamlit run app.py"""

import sys
from pathlib import Path

import streamlit as st

# let us import this project's own modules
sys.path.insert(0, str(Path(__file__).parent))

from resume_builder import run_resume_builder

st.set_page_config(page_title="Resume Builder", page_icon="📄")

st.title("📄 AI Resume Builder")
st.caption("Add your experience and a job post. 5 AI agents write a tailored resume + cover letter. (Free Groq model)")

SAMPLE_DIR = Path(__file__).parent / "sample_input"

# pre-fill with the sample files so it is easy to try
exp_sample = (SAMPLE_DIR / "raw_experience.txt").read_text(encoding="utf-8")
job_sample = (SAMPLE_DIR / "job_description.txt").read_text(encoding="utf-8")

col1, col2 = st.columns(2)
with col1:
    experience = st.text_area("Your experience", value=exp_sample, height=300)
with col2:
    job = st.text_area("Job description", value=job_sample, height=300)

if st.button("Build Resume", type="primary"):
    if not experience.strip() or not job.strip():
        st.warning("Please fill in both boxes.")
    else:
        try:
            with st.spinner("Agents are writing... this can take a minute."):
                result = run_resume_builder(experience, job)
            st.success("Done!")
            st.markdown(result)
            st.download_button("Download", result, file_name="resume.md")
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower() or "queue" in str(e).lower():
                st.error("The AI server is busy right now. Wait a few seconds and try again.")
            else:
                st.error(f"Something went wrong: {e}")
