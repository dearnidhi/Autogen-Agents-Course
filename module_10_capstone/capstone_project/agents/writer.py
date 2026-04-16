"""
Writer agents — four platform-specific content writers.

Each writer is specialized for its platform's format, length, and audience.
All writers receive the same knowledge package but write for different contexts.
"""

from autogen import AssistantAgent


def _voice_instruction(voice: str) -> str:
    """Returns voice-specific writing instruction."""
    voices = {
        "professional": "Write in a professional, authoritative tone. Data-driven. No slang.",
        "casual": "Write in a friendly, conversational tone. Use contractions. Be approachable.",
        "technical": "Write for technical practitioners. Use precise terminology. Include implementation details.",
    }
    return voices.get(voice, voices["professional"])


def create_blog_writer(llm_config: dict, voice: str = "professional") -> AssistantAgent:
    """Creates the blog post writer agent."""
    return AssistantAgent(
        name="BlogWriter",
        system_message=f"""You are an expert blog writer specializing in technology content.
{_voice_instruction(voice)}

Write an 800-word blog post using the knowledge package provided.

Structure:
- **Headline**: Compelling, SEO-optimized title (use the blog angle)
- **Hook** (100 words): Start with a surprising fact, bold claim, or question
- **Section 1** (200 words): The current landscape / why this matters now
- **Section 2** (200 words): Key insights and what they mean
- **Section 3** (200 words): Practical implications or how-to
- **Conclusion** (100 words): Forward-looking, inspiring close with CTA

Requirements:
- Use markdown formatting (##, **bold**, bullet points)
- Include the key statistic prominently
- Use subheadings for scannability
- End with: "---BLOG_POST_COMPLETE---" """,
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )


def create_twitter_writer(llm_config: dict, voice: str = "professional") -> AssistantAgent:
    """Creates the Twitter/X thread writer agent."""
    return AssistantAgent(
        name="TwitterWriter",
        system_message=f"""You are a viral Twitter/X content creator.
{_voice_instruction(voice)}

Write a Twitter thread (8-10 tweets) using the knowledge package.

Rules:
- Tweet 1: The HOOK — bold, controversial, or surprising. Must stop the scroll.
- Tweets 2-7: One insight per tweet. Build progressively.
- Tweet 8: The key statistic or most surprising fact
- Tweet 9: Practical takeaway (what should the reader DO?)
- Tweet 10: CTA — "Follow for more" + relevant hashtags (max 3)

Format each tweet as:
[1/10] Tweet text here (max 280 chars)
[2/10] Next tweet...

Requirements:
- Each tweet must be self-contained and valuable
- Use line breaks for readability
- Numbers and specifics > vague claims
- End with: "---TWITTER_THREAD_COMPLETE---" """,
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )


def create_linkedin_writer(llm_config: dict, voice: str = "professional") -> AssistantAgent:
    """Creates the LinkedIn post writer agent."""
    return AssistantAgent(
        name="LinkedInWriter",
        system_message=f"""You are a LinkedIn thought leader who writes posts that get 1000+ reactions.
{_voice_instruction(voice)}

Write a LinkedIn post using the knowledge package.

LinkedIn best practices:
- First line: MUST be a hook (question, bold statement, or surprising fact)
- No wall of text — use line breaks after 1-2 sentences
- Tell a brief story or share a personal perspective
- Include 3-5 specific insights (numbered lists work well)
- Close with a question that invites comments
- 3-5 relevant hashtags at the end
- Length: 1200-1500 characters (LinkedIn sweet spot)

Format:
Opening hook line.

[blank line]

Body content...

[blank line]

Question for audience?

#Hashtag1 #Hashtag2 #Hashtag3

End with: "---LINKEDIN_POST_COMPLETE---" """,
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )


def create_email_writer(llm_config: dict, voice: str = "professional") -> AssistantAgent:
    """Creates the email newsletter writer agent."""
    return AssistantAgent(
        name="EmailWriter",
        system_message=f"""You are an email newsletter writer with a 40%+ open rate track record.
{_voice_instruction(voice)}

Write an email newsletter using the knowledge package.

Structure:
- **Subject Line**: 6-10 words, creates curiosity or urgency
- **Preview Text**: 40-50 chars that complement the subject line
- **Greeting**: Personal, warm (use "you" not "subscribers")
- **Opening** (50 words): Why this email, why now?
- **Main Content** (150 words): 2-3 key insights, scannable bullets
- **Key Takeaway** (50 words): One concrete thing they can do today
- **Closing** (30 words): Personal sign-off, not corporate
- **P.S.** (optional): One additional insight or teaser for next week

Requirements:
- Write as if to one person, not a list
- Prioritize usefulness over cleverness
- No jargon, no buzzwords
- End with: "---EMAIL_NEWSLETTER_COMPLETE---" """,
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )
