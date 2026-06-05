"""Simple web UI for the AI Startup Idea Validator. Run: streamlit run app.py"""

import sys
from pathlib import Path

import streamlit as st

# let us import this project's own modules
sys.path.insert(0, str(Path(__file__).parent))

from validator import validate_idea

st.set_page_config(page_title="Startup Validator", page_icon="🚀")

st.title("🚀 AI Startup Idea Validator")
st.caption("Describe your idea. 4 AI experts judge it, then a verdict + score. (Free Groq model)")

idea = st.text_area("Your startup idea", height=120,
                    placeholder="e.g. An app that matches old clothes with local thrift buyers for cash.")

if st.button("Validate Idea", type="primary"):
    if not idea.strip():
        st.warning("Please describe your idea first.")
    else:
        try:
            with st.spinner("4 experts are reviewing your idea..."):
                r = validate_idea(idea)

            # Big score + verdict on top
            if r["score"] is not None:
                st.metric("Score", f"{r['score']} / 10")
            st.markdown("### Verdict")
            st.markdown(r["verdict"] or "(empty — try again)")

            st.markdown("### What each expert said")
            t1, t2, t3, t4 = st.tabs(["📈 Market", "🙋 Customer", "🔥 Risks", "💰 Money"])
            with t1:
                st.markdown(r["market"] or "(empty)")
            with t2:
                st.markdown(r["customer"] or "(empty)")
            with t3:
                st.markdown(r["skeptic"] or "(empty)")
            with t4:
                st.markdown(r["money"] or "(empty)")

            full = (f"# {idea}\n\n## Verdict\n{r['verdict']}\n\n## Market\n{r['market']}\n\n"
                    f"## Customer\n{r['customer']}\n\n## Risks\n{r['skeptic']}\n\n## Money\n{r['money']}")
            st.download_button("Download full report", full, file_name="validation.md")
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                st.error("The AI server is busy right now. Wait a few seconds and try again.")
            else:
                st.error(f"Something went wrong: {e}")
