"""Data processing utilities for the Content Factory."""

import re


def count_tokens_estimate(text: str) -> int:
    """Estimates token count (rough: 4 chars ≈ 1 token)."""
    return len(text) // 4


def count_tweets(thread_text: str) -> int:
    """Counts tweets in a numbered thread."""
    pattern = r'\[\d+/\d+\]'
    return len(re.findall(pattern, thread_text))


def extract_hashtags(text: str) -> list[str]:
    """Extracts hashtags from text."""
    return re.findall(r'#\w+', text)


def word_count(text: str) -> int:
    """Returns word count."""
    return len(text.split())


def truncate_for_context(text: str, max_words: int = 1500) -> str:
    """Truncates text to stay within context limits."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "\n[...truncated...]"


def clean_content(text: str) -> str:
    """Removes internal markers from final content."""
    markers = [
        "---BLOG_POST_COMPLETE---",
        "---TWITTER_THREAD_COMPLETE---",
        "---LINKEDIN_POST_COMPLETE---",
        "---EMAIL_NEWSLETTER_COMPLETE---",
        "RESEARCH_DONE",
        "RESEARCH_PACKAGE_COMPLETE",
        "CONTENT_APPROVED",
        "FACTORY_COMPLETE",
    ]
    for marker in markers:
        text = text.replace(marker, "").strip()
    return text
