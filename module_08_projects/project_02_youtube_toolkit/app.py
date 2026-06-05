"""Simple web UI for the YouTube Creator Toolkit. Run: streamlit run app.py"""

import sys
from pathlib import Path

import streamlit as st

# let us import this project's own modules
sys.path.insert(0, str(Path(__file__).parent))

from youtube_toolkit import run_toolkit

st.set_page_config(page_title="YouTube Toolkit", page_icon="🎬")

st.title("🎬 YouTube Creator Toolkit")
st.caption("One topic -> titles, full script, description, tags & thumbnail text. (Free Groq model)")

topic = st.text_input("Video topic", placeholder="e.g. How to learn Python in 2025")
tone = st.radio("Tone", ["energetic", "calm", "funny", "professional"], horizontal=True)

if st.button("Generate Content Kit", type="primary"):
    if not topic.strip():
        st.warning("Please type a video topic first.")
    else:
        try:
            with st.spinner("Agents are creating your content kit... about a minute."):
                r = run_toolkit(topic, tone=tone)
            st.success("Done! Saved in the output/ folder.")

            t1, t2, t3, t4 = st.tabs(["🎯 Titles", "📜 Script", "🔍 SEO", "🧠 Strategy"])
            with t1:
                st.markdown(r["titles"] or "(empty — try again)")
            with t2:
                st.markdown(r["script"] or "(empty — try again)")
            with t3:
                st.markdown(r["seo"] or "(empty — try again)")
            with t4:
                st.markdown(r["strategy"] or "(empty — try again)")

            full = (f"# {topic}\n\n## Titles\n{r['titles']}\n\n## Script\n{r['script']}"
                    f"\n\n## SEO\n{r['seo']}")
            st.download_button("Download everything", full, file_name="content_kit.md")
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                st.error("The AI server is busy right now. Wait a few seconds and try again.")
            else:
                st.error(f"Something went wrong: {e}")
