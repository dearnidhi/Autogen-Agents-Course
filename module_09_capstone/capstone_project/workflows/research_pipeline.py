"""Stage 1 — one researcher agent turns the topic into a knowledge package."""

import os
import sys
import re
# Make the project folder importable so "agents" and "llm" resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import get_llm_config
from agents.researcher import create_researcher


def run_research_pipeline(topic: str, provider: str = None) -> str:
    """Ask one researcher for facts, stats and angles. Fast — a single call."""
    print(f"\n--- Researching: {topic} ---")

    llm_config = get_llm_config(provider=provider, temperature=0.4)
    llm_config["max_tokens"] = 800

    researcher = create_researcher(llm_config)
    reply = researcher.generate_reply(messages=[{"role": "user",
        "content": f"Research this topic for a content campaign:\n{topic}"}])
    if isinstance(reply, dict):
        reply = reply.get("content", "")
    package = re.sub(r"RESEARCH_DONE.*", "", (reply or "")).strip()

    print(f"--- Knowledge package: {len(package.split())} words ---")
    return package
