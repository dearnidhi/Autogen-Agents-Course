"""Publisher — confirms the content and saves it to files."""

import re
import json
from pathlib import Path
from datetime import datetime
from autogen import AssistantAgent


def create_publisher(llm_config: dict, output_dir: Path) -> AssistantAgent:
    """Confirms all pieces are done and writes a short summary."""
    return AssistantAgent(
        name="Publisher",
        system_message=f"""You are the publisher.

After the review, check that all 4 pieces are present (blog, twitter thread,
linkedin post, email newsletter). Then write a short summary:

---PRODUCTION SUMMARY---
Output: {output_dir}
Files: blog_post.md, twitter_thread.md, linkedin_post.md, email_newsletter.md
Quality: [APPROVED / NEEDS_REVISION]
When to post: [a quick suggestion for each piece]
---END SUMMARY---

End with: FACTORY_COMPLETE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )


# Helpers used by the workflow after the chat ends

def extract_content_blocks(messages: list) -> dict:
    """Pulls each content piece out of the chat using its end marker."""
    content = {"blog_post": "", "twitter_thread": "", "linkedin_post": "", "email_newsletter": ""}
    markers = {
        "blog_post": "---BLOG_POST_COMPLETE---",
        "twitter_thread": "---TWITTER_THREAD_COMPLETE---",
        "linkedin_post": "---LINKEDIN_POST_COMPLETE---",
        "email_newsletter": "---EMAIL_NEWSLETTER_COMPLETE---",
    }
    for msg in messages:
        text = msg.get("content", "")
        for key, marker in markers.items():
            if marker in text and not content[key]:
                content[key] = text[:text.find(marker)].strip()
    return content


def extract_knowledge_package(messages: list) -> str:
    """Pulls the knowledge package out of the research chat."""
    start_m, end_m = "---KNOWLEDGE PACKAGE START---", "---KNOWLEDGE PACKAGE END---"
    for msg in messages:
        text = msg.get("content", "")
        if start_m in text and end_m in text:
            start, end = text.find(start_m), text.find(end_m)
            return text[start:end + len(end_m)]
    return ""


def save_all_outputs(topic, content, output_base, knowledge_package="") -> Path:
    """Saves all pieces to a timestamped folder and returns its path."""
    slug = re.sub(r"\s+", "_", re.sub(r"[^\w\s-]", "", topic.lower()).strip())[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_base / f"{slug}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    for key, filename in {
        "blog_post": "blog_post.md",
        "twitter_thread": "twitter_thread.md",
        "linkedin_post": "linkedin_post.md",
        "email_newsletter": "email_newsletter.md",
    }.items():
        if content.get(key):
            (output_dir / filename).write_text(content[key], encoding="utf-8")

    if knowledge_package:
        (output_dir / "knowledge_package.md").write_text(knowledge_package, encoding="utf-8")

    return output_dir
