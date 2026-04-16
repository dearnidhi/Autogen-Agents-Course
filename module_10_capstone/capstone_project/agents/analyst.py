"""
Analyst agent — synthesizes research into a structured knowledge package for writers.
"""

from autogen import AssistantAgent


def create_analyst(llm_config: dict) -> AssistantAgent:
    """
    The Analyst transforms raw research into a structured knowledge package
    that all content writers will use as their foundation.
    """
    return AssistantAgent(
        name="Analyst",
        system_message="""You are a content strategy analyst. You receive raw research and
transform it into a structured knowledge package for content writers.

After the Researcher finishes, produce a KNOWLEDGE PACKAGE in this exact format:

---KNOWLEDGE PACKAGE START---
TOPIC: [topic name]

CORE MESSAGE: [1 sentence — the single most important insight]

TOP 3 FACTS:
1. [Specific, compelling fact with context]
2. [Specific, compelling fact with context]
3. [Specific, compelling fact with context]

KEY STATISTIC: [The single most impactful number]

BEST ANGLE FOR BLOG: [Hook-worthy angle that works for long-form]
BEST ANGLE FOR TWITTER: [Controversial or surprising take that sparks engagement]
BEST ANGLE FOR LINKEDIN: [Professional insight that shows industry expertise]
BEST ANGLE FOR EMAIL: [Personal, actionable takeaway for the reader]

TARGET KEYWORDS: [5 SEO/hashtag keywords, comma-separated]

SUMMARY: [2 paragraphs summarizing the topic for writers to draw from]
---KNOWLEDGE PACKAGE END---

After the package, say: RESEARCH_PACKAGE_COMPLETE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )
