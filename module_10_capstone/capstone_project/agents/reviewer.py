"""
Brand Reviewer agent — ensures all content matches the brand voice and is consistent.
"""

from autogen import AssistantAgent


def create_brand_reviewer(llm_config: dict, voice: str = "professional") -> AssistantAgent:
    """
    The Brand Reviewer checks all 4 content pieces for:
    - Consistent brand voice
    - Factual consistency (same stats used everywhere)
    - Platform appropriateness
    - Quality standards
    """
    voice_criteria = {
        "professional": "authoritative, data-driven, formal, no slang or contractions",
        "casual": "friendly, conversational, approachable, uses contractions and everyday language",
        "technical": "precise, uses correct technical terms, assumes expertise, includes specifics",
    }
    criteria = voice_criteria.get(voice, voice_criteria["professional"])

    return AssistantAgent(
        name="BrandReviewer",
        system_message=f"""You are the Editor-in-Chief and Brand Guardian.
Required brand voice: {voice.upper()} — {criteria}

After all 4 content writers have finished, review ALL content for:

1. **Voice Consistency**: Does each piece match the {voice} voice?
2. **Factual Consistency**: Are the same statistics used correctly across pieces?
3. **Platform Fit**: Is each piece truly native to its platform?
4. **Quality Bar**: Would a professional be proud to publish this?

For each piece, give:
- ✓ APPROVED (if ready to publish)
- ✗ NEEDS FIX: [specific issue] (if not)

After reviewing all 4 pieces, summarize:
"BRAND REVIEW COMPLETE. X/4 pieces approved."

Then say: CONTENT_APPROVED — Publisher, please save all outputs.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=3,
    )
