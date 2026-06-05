"""Platform-specific content formatting utilities."""

import re


def format_for_platform(content: str, platform: str) -> str:
    """Applies platform-specific formatting to content."""
    formatters = {
        "blog": _format_blog,
        "twitter": _format_twitter,
        "linkedin": _format_linkedin,
        "email": _format_email,
    }
    formatter = formatters.get(platform.lower(), lambda x: x)
    return formatter(content)


def _format_blog(content: str) -> str:
    """Ensures blog content has proper markdown structure."""
    # Ensure there's a title
    lines = content.strip().split("\n")
    if lines and not lines[0].startswith("#"):
        content = "# " + lines[0] + "\n\n" + "\n".join(lines[1:])
    return content


def _format_twitter(content: str) -> str:
    """Ensures each tweet is properly formatted and within limits."""
    lines = content.strip().split("\n")
    formatted = []
    for line in lines:
        if line.strip() and len(line) > 280:
            # Truncate long tweets
            line = line[:277] + "..."
        formatted.append(line)
    return "\n".join(formatted)


def _format_linkedin(content: str) -> str:
    """Formats LinkedIn post — ensures proper spacing."""
    # LinkedIn renders line breaks as paragraph breaks
    # Double-space for readability
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def _format_email(content: str) -> str:
    """Formats email with proper sections."""
    return content.strip()


def add_metadata_header(content: str, platform: str, topic: str, voice: str) -> str:
    """Adds a metadata comment header to saved files."""
    from datetime import datetime
    header = f"""---
platform: {platform}
topic: {topic}
voice: {voice}
generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
---

"""
    return header + content
