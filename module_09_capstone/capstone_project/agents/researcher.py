"""Researcher agent — gathers facts and ideas about the topic."""

from autogen import AssistantAgent


def create_researcher(llm_config: dict) -> AssistantAgent:
    """Gathers facts, stats, and angles about the topic."""
    return AssistantAgent(
        name="Researcher",
        system_message="""You are a research expert in tech and business.

For the given topic, list:
1. Key facts (5-7)
2. Statistics or numbers (3-5)
3. Current trends
4. Expert opinions (2-3)
5. Good content angles (3)
6. Common myths (1-2)
7. Future outlook

Be specific and use real examples.
End with: RESEARCH_DONE — Analyst, please summarize.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )
