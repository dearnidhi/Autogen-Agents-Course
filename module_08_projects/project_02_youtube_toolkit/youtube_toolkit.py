"""Turn one video topic into titles, a full script, and SEO — a YouTube content kit."""

import re
import argparse
from pathlib import Path
from datetime import datetime

from llm import get_llm_config
from agents import create_toolkit_agents

OUTPUT_DIR = Path(__file__).parent / "output"


def _ask(agent, prompt: str) -> str:
    """Send one prompt to one agent and return its reply text."""
    reply = agent.generate_reply(messages=[{"role": "user", "content": prompt}])
    if isinstance(reply, dict):
        reply = reply.get("content", "")
    return (reply or "").strip()


def run_toolkit(topic: str, tone: str = "energetic") -> dict:
    """Run the 4 agents one by one and return the full content kit."""
    llm_config = get_llm_config(temperature=0.7)
    llm_config["max_tokens"] = 1200  # keep replies short and fast
    agents = create_toolkit_agents(llm_config, tone)

    # 1. Strategist plans the angle, audience and hook
    strategy = _ask(agents["strategist"], f"Topic: {topic}")

    # 2-4. Each writer uses the topic + strategy
    context = f"Topic: {topic}\n\nStrategy:\n{strategy}"
    titles = _ask(agents["title"], context)
    script = _ask(agents["script"], context)
    seo = _ask(agents["seo"], context)

    result = {"topic": topic, "strategy": strategy,
              "titles": titles, "script": script, "seo": seo}
    _save(result)
    return result


def _save(result: dict) -> None:
    """Save the whole kit to one markdown file."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    #learn_python_fast
    slug = re.sub(r"[^\w]+", "_", result["topic"].lower()).strip("_")[:40]
    #20260607_143000
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    text = (f"# {result['topic']}\n\n## Strategy\n{result['strategy']}\n\n"
            f"## Titles\n{result['titles']}\n\n## Script\n{result['script']}\n\n"
            f"## SEO\n{result['seo']}\n")
    (OUTPUT_DIR / f"{slug}_{ts}.md").write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="YouTube Creator Toolkit")
    parser.add_argument("--topic", default="How to learn Python in 2025")
    parser.add_argument("--tone", default="energetic")
    args = parser.parse_args()

    result = run_toolkit(args.topic, tone=args.tone)
    for key in ("strategy", "titles", "script", "seo"):
        print(f"\n===== {key.upper()} =====\n{result[key]}")


if __name__ == "__main__":
    main()

    