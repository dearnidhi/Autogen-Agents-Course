"""The 4 agents that turn one topic into a full YouTube content kit."""

from autogen import AssistantAgent


def create_toolkit_agents(llm_config: dict, tone: str = "energetic") -> dict:
    """Make the strategist, title writer, script writer and SEO writer."""

    strategist = AssistantAgent(
        name="Strategist",
        system_message=f"""Plan a YouTube video (tone: {tone}). Give 3 bullets only:
        ANGLE (how to stand out), AUDIENCE (who it's for), HOOK (one opening line).""",
        llm_config=llm_config,
    )

    title_writer = AssistantAgent(
        name="TitleWriter",
        system_message=f"""Write 5 catchy YouTube titles (tone: {tone}), each under
        60 characters. Numbered list, titles only.""",
        llm_config=llm_config,
    )

    script_writer = AssistantAgent(
        name="ScriptWriter",
        system_message=f"""Write a full YouTube script (tone: {tone}), spoken style.
        Parts: HOOK, INTRO, MAIN (3-4 points), OUTRO (summary + ask to like/subscribe).
        Script only.""",
        llm_config=llm_config,
    )

    seo_writer = AssistantAgent(
        name="SEOWriter",
        system_message=f"""Write YouTube SEO (tone: {tone}):
        DESCRIPTION (3-4 lines with keywords), TAGS (10, comma separated),
        HASHTAGS (5), THUMBNAIL TEXT (3 short phrases, max 4 words each).""",
        llm_config=llm_config,
    )

    return {
        "strategist": strategist,
        "title": title_writer,
        "script": script_writer,
        "seo": seo_writer,
    }
