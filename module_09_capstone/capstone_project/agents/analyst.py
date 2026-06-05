"""Analyst agent — turns research into a simple package for the writers."""

from autogen import AssistantAgent


def create_analyst(llm_config: dict) -> AssistantAgent:
    """Turns raw research into a clear knowledge package."""
    return AssistantAgent(
        name="Analyst",
        system_message="""You are a content strategist. Take the research and turn it into
a knowledge package the writers will use.

Use this exact format:

---KNOWLEDGE PACKAGE START---
TOPIC: [topic]

CORE MESSAGE: [the single most important idea, one sentence]

TOP 3 FACTS:
1. [fact]
2. [fact]
3. [fact]

KEY STATISTIC: [the most striking number]

BLOG ANGLE: [angle for a long blog post]
TWITTER ANGLE: [surprising take for a thread]
LINKEDIN ANGLE: [professional insight]
EMAIL ANGLE: [useful, personal takeaway]

KEYWORDS: [5 keywords, comma-separated]

SUMMARY: [2 short paragraphs the writers can draw from]
---KNOWLEDGE PACKAGE END---

After the package, say: RESEARCH_PACKAGE_COMPLETE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )
