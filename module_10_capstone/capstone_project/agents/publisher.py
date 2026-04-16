"""
Publisher agent — extracts and saves all content to output files.
"""

import re
import json
from pathlib import Path
from datetime import datetime
from autogen import AssistantAgent


def create_publisher(llm_config: dict, output_dir: Path) -> AssistantAgent:
    """
    The Publisher extracts content from the conversation and saves it to files.
    This simulates a "publish to CMS" step in a real content pipeline.
    """
    return AssistantAgent(
        name="Publisher",
        system_message=f"""You are the Content Publisher.

After the Brand Reviewer approves the content, your job is to:

1. Confirm all 4 content pieces are complete:
   - Blog post (look for ---BLOG_POST_COMPLETE---)
   - Twitter thread (look for ---TWITTER_THREAD_COMPLETE---)
   - LinkedIn post (look for ---LINKEDIN_POST_COMPLETE---)
   - Email newsletter (look for ---EMAIL_NEWSLETTER_COMPLETE---)

2. Produce a PRODUCTION SUMMARY in this format:

---PRODUCTION SUMMARY---
Output Directory: {output_dir}
Files Generated:
- blog_post.md (approx [N] words)
- twitter_thread.md ([N] tweets)
- linkedin_post.md (approx [N] chars)
- email_newsletter.md (approx [N] words)

Content Quality: [APPROVED / NEEDS_REVISION]
Estimated Reach: [Blog: SEO potential | Twitter: thread format | LinkedIn: engagement | Email: subscriber value]
Recommended Posting Schedule: [Suggest when to post each piece]
---END SUMMARY---

End with: FACTORY_COMPLETE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )


# ============================================================
# File saving utilities (called from main.py after conversation)
# ============================================================

def extract_content_blocks(messages: list) -> dict:
    """
    Extracts the 4 content pieces from GroupChat messages.
    Looks for the completion markers to identify each piece.
    """
    content = {
        "blog_post": "",
        "twitter_thread": "",
        "linkedin_post": "",
        "email_newsletter": "",
    }

    markers = {
        "blog_post": ("---BLOG_POST_COMPLETE---", "BlogWriter"),
        "twitter_thread": ("---TWITTER_THREAD_COMPLETE---", "TwitterWriter"),
        "linkedin_post": ("---LINKEDIN_POST_COMPLETE---", "LinkedInWriter"),
        "email_newsletter": ("---EMAIL_NEWSLETTER_COMPLETE---", "EmailWriter"),
    }

    for msg in messages:
        msg_content = msg.get("content", "")
        msg_name = msg.get("name", "")

        for content_type, (marker, agent_name) in markers.items():
            if marker in msg_content and not content[content_type]:
                # Extract content before the marker
                block = msg_content[:msg_content.find(marker)].strip()
                content[content_type] = block

    return content


def extract_knowledge_package(messages: list) -> str:
    """Extracts the knowledge package from research pipeline messages."""
    for msg in messages:
        text = msg.get("content", "")
        if "---KNOWLEDGE PACKAGE START---" in text:
            start = text.find("---KNOWLEDGE PACKAGE START---")
            end = text.find("---KNOWLEDGE PACKAGE END---")
            if end > start:
                return text[start:end + len("---KNOWLEDGE PACKAGE END---")]
    return ""


def save_all_outputs(
    topic: str,
    content: dict,
    output_base: Path,
    knowledge_package: str = "",
) -> Path:
    """
    Saves all content pieces to a timestamped output directory.

    Returns:
        Path to the output directory
    """
    # Create output directory
    slug = re.sub(r"[^\w\s-]", "", topic.lower())
    slug = re.sub(r"\s+", "_", slug.strip())[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_base / f"{slug}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save each content piece
    file_map = {
        "blog_post": "blog_post.md",
        "twitter_thread": "twitter_thread.md",
        "linkedin_post": "linkedin_post.md",
        "email_newsletter": "email_newsletter.md",
    }

    saved_files = []
    for content_type, filename in file_map.items():
        text = content.get(content_type, "")
        if text:
            filepath = output_dir / filename
            filepath.write_text(text, encoding="utf-8")
            saved_files.append(filename)

    # Save knowledge package
    if knowledge_package:
        kp_path = output_dir / "knowledge_package.md"
        kp_path.write_text(knowledge_package, encoding="utf-8")

    # Save production summary
    summary = {
        "topic": topic,
        "generated_at": datetime.now().isoformat(),
        "output_directory": str(output_dir),
        "files_generated": saved_files,
        "word_counts": {
            ct: len(content.get(ct, "").split())
            for ct in file_map
        },
    }

    summary_path = output_dir / "production_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    return output_dir
