"""
module_08_projects/project_01_research_assistant/utils.py
----------------------------------------------------------
Utility functions for the Research Assistant project.
"""

import re
from datetime import datetime
from pathlib import Path


def clean_topic(topic: str) -> str:
    """Sanitizes a topic string for use in filenames."""
    cleaned = re.sub(r"[^\w\s-]", "", topic.lower())
    cleaned = re.sub(r"\s+", "_", cleaned.strip())
    return cleaned[:60]


def format_research_prompt(topic: str, depth: str = "comprehensive") -> str:
    """Creates a structured research prompt for the Researcher agent."""
    return f"""Research Topic: {topic}

Depth: {depth}
Date: {datetime.now().strftime('%B %Y')}

Please research this topic thoroughly. Include:
1. Overview and background
2. Current state / recent developments
3. Key statistics and data points
4. Main challenges or debates
5. Future outlook

Use specific facts, dates, and examples. Cite sources when possible."""


def extract_sections(report_text: str) -> dict:
    """Parses a markdown report into sections."""
    sections = {}
    current_section = "intro"
    current_lines = []

    for line in report_text.split("\n"):
        if line.startswith("## "):
            if current_lines:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = line[3:].strip().lower().replace(" ", "_")
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def word_count(text: str) -> int:
    """Returns approximate word count of text."""
    return len(text.split())


def truncate_to_tokens(text: str, max_words: int = 2000) -> str:
    """Truncates text to approximately max_words words."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "\n\n[... truncated for context length ...]"
