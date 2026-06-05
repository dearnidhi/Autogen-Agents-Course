"""Simple web UI for the AI Content Factory. Run: streamlit run app.py"""

import os
import sys
from pathlib import Path

import streamlit as st

# this folder must be on the path so main.py's imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_content_factory

st.set_page_config(page_title="Content Factory", page_icon="🏭")

st.title("🏭 AI Content Factory")
st.caption("One topic in. Blog + Twitter + LinkedIn + Email out. (Free Groq model)")

topic = st.text_input("Topic", placeholder="e.g. The rise of multi-agent AI")
voice = st.radio("Voice", ["professional", "casual", "technical"], horizontal=True)

if st.button("Create Content", type="primary"):
    if not topic.strip():
        st.warning("Please type a topic first.")
    else:
        try:
            with st.spinner("Agents are researching and writing... this takes a minute or two."):
                result = run_content_factory(topic=topic, voice=voice)
            st.success(f"Done! Saved in {result['output_dir']}")

            content = result["content"]
            tabs = st.tabs(["📝 Blog", "🐦 Twitter", "💼 LinkedIn", "✉️ Email"])
            keys = ["blog_post", "twitter_thread", "linkedin_post", "email_newsletter"]
            for tab, key in zip(tabs, keys):
                with tab:
                    text = content.get(key) or "(this piece came back empty — try again)"
                    st.markdown(text)
                    st.download_button("Download", text, file_name=f"{key}.md", key=key)
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                st.error("The AI server is busy right now. Wait a few seconds and try again.")
            else:
                st.error(f"Something went wrong: {e}")
