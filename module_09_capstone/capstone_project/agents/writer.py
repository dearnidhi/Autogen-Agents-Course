"""Writer agents — one writer per platform (blog, Twitter, LinkedIn, email)."""

from autogen import AssistantAgent


def _voice(voice: str) -> str:
    """Returns the tone instruction for the chosen voice."""
    voices = {
        "professional": "Use a professional, confident tone. No slang.",
        "casual": "Use a friendly, conversational tone. Contractions are fine.",
        "technical": "Write for experts. Use correct terms and details.",
    }
    return voices.get(voice, voices["professional"])


def create_blog_writer(llm_config: dict, voice: str = "professional") -> AssistantAgent:
    """Writes the blog post."""
    return AssistantAgent(
        name="BlogWriter",
        system_message=f"""You are a blog writer. {_voice(voice)}

Write an ~800-word blog post from the knowledge package. Use the BLOG ANGLE.

Include:
- A catchy title
- A strong opening hook
- 3 short sections with subheadings
- A closing with a call to action
- Markdown formatting and the key statistic

End with: ---BLOG_POST_COMPLETE---""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )


def create_twitter_writer(llm_config: dict, voice: str = "professional") -> AssistantAgent:
    """Writes the Twitter/X thread."""
    return AssistantAgent(
        name="TwitterWriter",
        system_message=f"""You are a Twitter/X writer. {_voice(voice)}

Write a thread of 8-10 tweets from the knowledge package. Use the TWITTER ANGLE.

Rules:
- Tweet 1 is the hook (make people stop scrolling)
- One idea per tweet, each under 280 characters
- Include the key statistic
- Last tweet: a takeaway + up to 3 hashtags

Format each line as: [1/10] tweet text

End with: ---TWITTER_THREAD_COMPLETE---""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )


def create_linkedin_writer(llm_config: dict, voice: str = "professional") -> AssistantAgent:
    """Writes the LinkedIn post."""
    return AssistantAgent(
        name="LinkedInWriter",
        system_message=f"""You are a LinkedIn writer. {_voice(voice)}

Write a LinkedIn post from the knowledge package. Use the LINKEDIN ANGLE.

Rules:
- First line is a hook
- Short lines, lots of white space
- 3-5 clear insights
- End with a question, then 3-5 hashtags
- Around 1200-1500 characters

End with: ---LINKEDIN_POST_COMPLETE---""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )


def create_email_writer(llm_config: dict, voice: str = "professional") -> AssistantAgent:
    """Writes the email newsletter."""
    return AssistantAgent(
        name="EmailWriter",
        system_message=f"""You are an email newsletter writer. {_voice(voice)}

Write a short newsletter from the knowledge package. Use the EMAIL ANGLE.

Include:
- A subject line that creates curiosity
- A warm greeting (talk to one person, use "you")
- 2-3 key insights as bullets
- One clear action the reader can take today
- A friendly sign-off

End with: ---EMAIL_NEWSLETTER_COMPLETE---""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )
