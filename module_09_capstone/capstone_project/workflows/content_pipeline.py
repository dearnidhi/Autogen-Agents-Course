"""Stage 2 — 4 writers each write one content piece from the knowledge package."""

import os
import re
import sys
from pathlib import Path
# Make the project folder importable so "agents" and "llm" resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import get_llm_config
from agents.writer import (
    create_blog_writer,
    create_twitter_writer,
    create_linkedin_writer,
    create_email_writer,
)
from agents.publisher import save_all_outputs


def _ask(agent, prompt: str) -> str:
    """Send one prompt to one agent and return its reply text."""
    reply = agent.generate_reply(messages=[{"role": "user", "content": prompt}])
    if isinstance(reply, dict):
        reply = reply.get("content", "")
    # strip the ---XXX_COMPLETE--- marker the writer adds
    return re.sub(r"-{0,3}[A-Z_]+_COMPLETE-{0,3}", "", reply or "").strip()


def run_content_pipeline(topic, knowledge_package, voice="professional",
                         provider=None, output_dir=None) -> dict:
    """Call each writer once (fast, no group chat) and save all 4 pieces."""
    print(f"\n--- Writing content (voice: {voice}) ---")

    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "output"

    llm_config = get_llm_config(provider=provider, temperature=0.7)
    llm_config["max_tokens"] = 1200

    context = f"TOPIC: {topic}\nVOICE: {voice.upper()}\n\n{knowledge_package}"

    writers = {
        "blog_post": create_blog_writer(llm_config, voice),
        "twitter_thread": create_twitter_writer(llm_config, voice),
        "linkedin_post": create_linkedin_writer(llm_config, voice),
        "email_newsletter": create_email_writer(llm_config, voice),
    }
    content = {key: _ask(agent, context) for key, agent in writers.items()}

    saved_dir = save_all_outputs(topic, content, output_dir, knowledge_package)
    print(f"\n--- Saved to: {saved_dir} ---")
    for key, text in content.items():
        print(f"  [{'ok' if text else '--'}] {key}.md")

    return {"content": content, "output_dir": saved_dir, "topic": topic, "voice": voice}
