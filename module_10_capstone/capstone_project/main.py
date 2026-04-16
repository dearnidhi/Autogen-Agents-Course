"""
module_10_capstone/capstone_project/main.py
--------------------------------------------
AI Content Factory — Main Entry Point

Takes a single topic and produces a complete multi-platform content package:
  - 800-word blog post
  - Twitter/X thread (8-10 tweets)
  - LinkedIn post
  - Email newsletter

This capstone integrates every AutoGen concept from the course:
  Modules 01-09: Agents, providers, tools, GroupChat, memory, custom agents, logging

Usage:
    python module_10_capstone/capstone_project/main.py \\
        --topic "The Rise of Multi-Agent AI Systems"

    python module_10_capstone/capstone_project/main.py \\
        --topic "Python for Data Science in 2025" \\
        --voice casual \\
        --provider gemini

    python module_10_capstone/capstone_project/main.py \\
        --topic "Building Production AI Agents" \\
        --voice technical \\
        --skip-research  # Use cached research if available
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.llm_config import get_llm_config, print_current_config


OUTPUT_DIR = Path(__file__).parent / "output"
CACHE_DIR = Path(__file__).parent / ".cache"


def get_cached_research(topic: str) -> str | None:
    """Returns cached research if available for this topic."""
    if not CACHE_DIR.exists():
        return None
    cache_key = topic.lower().replace(" ", "_")[:50]
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        data = json.loads(cache_file.read_text())
        print(f"  Using cached research from {data.get('cached_at', 'unknown date')}")
        return data.get("knowledge_package")
    return None


def cache_research(topic: str, knowledge_package: str):
    """Saves research to cache for reuse."""
    from datetime import datetime
    CACHE_DIR.mkdir(exist_ok=True)
    cache_key = topic.lower().replace(" ", "_")[:50]
    cache_file = CACHE_DIR / f"{cache_key}.json"
    cache_file.write_text(json.dumps({
        "topic": topic,
        "knowledge_package": knowledge_package,
        "cached_at": datetime.now().isoformat(),
    }, indent=2))


def run_content_factory(
    topic: str,
    voice: str = "professional",
    provider: str = None,
    skip_research: bool = False,
) -> dict:
    """
    Runs the complete AI Content Factory pipeline.

    Pipeline:
    1. Research Stage: Orchestrator → Researcher → Analyst → Knowledge Package
    2. Content Stage: BlogWriter → TwitterWriter → LinkedInWriter → EmailWriter
                     → BrandReviewer → Publisher → Output Files

    Args:
        topic: The topic to create content about
        voice: Brand voice ("professional", "casual", "technical")
        provider: LLM provider override
        skip_research: If True, use cached research if available

    Returns:
        dict with content pieces, output directory, and metadata
    """
    print("\n" + "=" * 65)
    print("AI CONTENT FACTORY")
    print("=" * 65)
    print(f"Topic    : {topic}")
    print(f"Voice    : {voice}")
    print(f"Provider : {provider or 'default (from .env)'}")
    print("=" * 65)
    print_current_config()

    # ──────────────────────────────────────────────
    # Stage 1: Research Pipeline
    # ──────────────────────────────────────────────
    knowledge_package = None

    if skip_research:
        knowledge_package = get_cached_research(topic)
        if knowledge_package:
            print("\n✓ Skipping research (using cache)")

    if not knowledge_package:
        print("\n[Stage 1/2] Starting Research Pipeline...")
        from workflows.research_pipeline import run_research_pipeline
        knowledge_package = run_research_pipeline(topic=topic, provider=provider)
        cache_research(topic, knowledge_package)

    if not knowledge_package:
        print("\n⚠ Warning: Research produced no output. Using topic description only.")
        knowledge_package = f"Topic: {topic}\n\nPlease create comprehensive content about this topic."

    # ──────────────────────────────────────────────
    # Stage 2: Content Pipeline
    # ──────────────────────────────────────────────
    print("\n[Stage 2/2] Starting Content Pipeline...")
    from workflows.content_pipeline import run_content_pipeline

    result = run_content_pipeline(
        topic=topic,
        knowledge_package=knowledge_package,
        voice=voice,
        provider=provider,
        output_dir=OUTPUT_DIR,
    )

    # ──────────────────────────────────────────────
    # Final Summary
    # ──────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("PRODUCTION COMPLETE")
    print("=" * 65)
    print(f"\nContent package for: '{topic}'")
    print(f"Output location: {result['output_dir']}")
    print("\nGenerated files:")
    output_dir = Path(result["output_dir"])
    for f in sorted(output_dir.glob("*.md")):
        wc = len(f.read_text().split())
        print(f"  {f.name:<35} {wc:>5} words")

    print("\nNext steps:")
    print("  1. Review the files in the output directory")
    print("  2. Make any edits for your specific audience")
    print("  3. Schedule posts using your preferred tools")
    print("\nCongratulations on completing the AutoGen Course! 🎉")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="AI Content Factory — Generate multi-platform content from a single topic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --topic "The Future of AI Coding Assistants"
  python main.py --topic "Python vs JavaScript for AI" --voice casual
  python main.py --topic "Building RAG Systems" --voice technical --provider gemini
  python main.py --topic "AI Productivity Tips" --skip-research
        """,
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="The Rise of Multi-Agent AI Systems in 2025",
        help="Topic to create content about",
    )
    parser.add_argument(
        "--voice",
        choices=["professional", "casual", "technical"],
        default="professional",
        help="Brand voice for all content pieces",
    )
    parser.add_argument(
        "--provider",
        choices=["groq", "gemini", "openrouter", "huggingface"],
        default=None,
        help="LLM provider (default: uses DEFAULT_PROVIDER from .env)",
    )
    parser.add_argument(
        "--skip-research",
        action="store_true",
        default=False,
        help="Skip research stage if cached results are available",
    )

    args = parser.parse_args()

    run_content_factory(
        topic=args.topic,
        voice=args.voice,
        provider=args.provider,
        skip_research=args.skip_research,
    )


if __name__ == "__main__":
    main()
