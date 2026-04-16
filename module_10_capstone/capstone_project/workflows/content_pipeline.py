"""
Content Pipeline — Stage 2 of the AI Content Factory.

Takes the knowledge package from Stage 1 and produces
4 platform-specific content pieces via specialist writer agents.
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from autogen import GroupChat, GroupChatManager, UserProxyAgent
from config.llm_config import get_llm_config
from ..agents.writer import (
    create_blog_writer,
    create_twitter_writer,
    create_linkedin_writer,
    create_email_writer,
)
from ..agents.reviewer import create_brand_reviewer
from ..agents.publisher import create_publisher, extract_content_blocks, save_all_outputs


def run_content_pipeline(
    topic: str,
    knowledge_package: str,
    voice: str = "professional",
    provider: str = None,
    output_dir: Path = None,
) -> dict:
    """
    Runs the content writing pipeline for all 4 platforms.

    Args:
        topic: Original topic string
        knowledge_package: Structured research from Stage 1
        voice: Brand voice ("professional", "casual", "technical")
        provider: Optional LLM provider override
        output_dir: Where to save output files

    Returns:
        dict with content pieces and output directory path
    """
    print("\n" + "=" * 60)
    print("Stage 2: Content Pipeline")
    print(f"Voice: {voice.upper()}")
    print("Agents: BlogWriter → TwitterWriter → LinkedInWriter → EmailWriter → BrandReviewer → Publisher")
    print("=" * 60)

    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "output"

    llm_config = get_llm_config(provider=provider, temperature=0.7)

    # Create all content agents
    admin = UserProxyAgent(
        name="ContentAdmin",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "FACTORY_COMPLETE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )

    blog_writer = create_blog_writer(llm_config, voice=voice)
    twitter_writer = create_twitter_writer(llm_config, voice=voice)
    linkedin_writer = create_linkedin_writer(llm_config, voice=voice)
    email_writer = create_email_writer(llm_config, voice=voice)
    brand_reviewer = create_brand_reviewer(llm_config, voice=voice)
    publisher = create_publisher(llm_config, output_dir=output_dir)

    # Content GroupChat — round_robin ensures each writer gets their turn
    groupchat = GroupChat(
        agents=[admin, blog_writer, twitter_writer, linkedin_writer, email_writer, brand_reviewer, publisher],
        messages=[],
        max_round=12,
        speaker_selection_method="round_robin",
    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: "FACTORY_COMPLETE" in msg.get("content", ""),
    )

    # Initial prompt with knowledge package
    initial_prompt = f"""CONTENT PRODUCTION BRIEF
Topic: {topic}
Voice: {voice.upper()}

{knowledge_package}

---

PRODUCTION INSTRUCTIONS:
1. BlogWriter: Write a full 800-word blog post using the Blog Angle above
2. TwitterWriter: Write a complete 10-tweet thread using the Twitter Angle
3. LinkedInWriter: Write a LinkedIn post using the LinkedIn Angle
4. EmailWriter: Write an email newsletter using the Email Angle
5. BrandReviewer: Review all 4 pieces for {voice} voice and quality
6. Publisher: Confirm completion and produce the production summary

All writers: Use the KNOWLEDGE PACKAGE above as your factual foundation.
All writers: Maintain the {voice.upper()} brand voice throughout."""

    print("\nStarting content production...\n")

    admin.initiate_chat(manager, message=initial_prompt)

    # Extract content from conversation
    messages = groupchat.messages
    content = extract_content_blocks(messages)

    # Save to files
    saved_dir = save_all_outputs(
        topic=topic,
        content=content,
        output_base=output_dir,
        knowledge_package=knowledge_package,
    )

    # Print summary
    print(f"\n{'='*60}")
    print("CONTENT FACTORY COMPLETE")
    print(f"{'='*60}")
    print(f"Output directory: {saved_dir}")
    for content_type, text in content.items():
        if text:
            wc = len(text.split())
            print(f"  ✓ {content_type}.md ({wc} words)")
        else:
            print(f"  ✗ {content_type}.md (not captured)")

    return {
        "content": content,
        "output_dir": saved_dir,
        "topic": topic,
        "voice": voice,
    }
