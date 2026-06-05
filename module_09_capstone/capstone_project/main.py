"""
AI Content Factory — Main Entry Point

Give it one topic. It researches the topic, then writes content for 4 platforms:
blog post, Twitter/X thread, LinkedIn post, and email newsletter.

Usage:
    python main.py --topic "The Rise of Multi-Agent AI Systems"
    python main.py --topic "Python for Data Science" --voice casual --provider gemini
"""

import os
import sys
import argparse
from pathlib import Path

# Make this project folder importable (standalone — no parent config needed)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm import print_current_config

OUTPUT_DIR = Path(__file__).parent / "output"


def run_content_factory(topic, voice="professional", provider=None):
    """Run the full pipeline: research the topic, then write all 4 content pieces."""
    print("\n" + "=" * 60)
    print("AI CONTENT FACTORY")
    print("=" * 60)
    print(f"Topic    : {topic}")
    print(f"Voice    : {voice}")
    print(f"Provider : {provider or 'default (from .env)'}")
    print("=" * 60)
    print_current_config()

    # Stage 1: research the topic
    print("\n[Stage 1/2] Researching...")
    from workflows.research_pipeline import run_research_pipeline
    knowledge_package = run_research_pipeline(topic=topic, provider=provider)

    if not knowledge_package:
        knowledge_package = f"Topic: {topic}\n\nWrite helpful content about this topic."

    # Stage 2: write the content
    print("\n[Stage 2/2] Writing content...")
    from workflows.content_pipeline import run_content_pipeline
    result = run_content_pipeline(
        topic=topic,
        knowledge_package=knowledge_package,
        voice=voice,
        provider=provider,
        output_dir=OUTPUT_DIR,
    )

    # Summary
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    print(f"Output: {result['output_dir']}")
    for f in sorted(Path(result["output_dir"]).glob("*.md")):
        print(f"  {f.name:<28} {len(f.read_text().split()):>5} words")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Generate multi-platform content from a single topic."
    )
    parser.add_argument(
        "--topic",
        default="The Rise of Multi-Agent AI Systems in 2025",
        help="Topic to create content about",
    )
    parser.add_argument(
        "--voice",
        choices=["professional", "casual", "technical"],
        default="professional",
        help="Tone for all content",
    )
    parser.add_argument(
        "--provider",
        choices=["groq", "openrouter", "cerebras"],
        default=None,
        help="LLM provider (default: from .env)",
    )

    args = parser.parse_args()
    run_content_factory(topic=args.topic, voice=args.voice, provider=args.provider)


if __name__ == "__main__":
    main()
