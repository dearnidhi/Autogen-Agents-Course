"""Brand Reviewer — checks all 4 pieces for the right tone and quality."""

from autogen import AssistantAgent


def create_brand_reviewer(llm_config: dict, voice: str = "professional") -> AssistantAgent:
    """Reviews all content for consistent voice and quality."""
    return AssistantAgent(
        name="BrandReviewer",
        system_message=f"""You are the editor. Required tone: {voice.upper()}.

After all 4 writers finish, check each piece for:
- Right tone ({voice})
- Same facts and numbers used everywhere
- Fits its platform
- Good enough to publish

For each piece, say APPROVED or NEEDS FIX: [reason].
Then say: "X/4 approved." and end with:
CONTENT_APPROVED — Publisher, please save the outputs.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=3,
    )
