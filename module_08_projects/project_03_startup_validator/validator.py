"""Validate a startup idea: 4 experts review it, a judge gives a score + verdict."""

import re
import argparse
from pathlib import Path
from datetime import datetime

from llm import get_llm_config, print_current_config
from agents import create_validator_agents

OUTPUT_DIR = Path(__file__).parent / "output"


def _ask(agent, prompt: str) -> str:
    """Send one prompt to one agent and return its reply text."""
    reply = agent.generate_reply(messages=[{"role": "user", "content": prompt}])
    if isinstance(reply, dict):
        reply = reply.get("content", "")
    return (reply or "").strip()


def validate_idea(idea: str, provider: str = None) -> dict:
    """Run the 4 experts + judge and return the full review."""
    llm_config = get_llm_config(provider=provider, temperature=0.6)
    llm_config["max_tokens"] = 700  # short, punchy reviews
    agents = create_validator_agents(llm_config)

    idea_prompt = f"Startup idea:\n{idea}"

    # 4 experts review the idea (each from their own angle)
    market = _ask(agents["market"], idea_prompt)
    customer = _ask(agents["customer"], idea_prompt)
    skeptic = _ask(agents["skeptic"], idea_prompt)
    money = _ask(agents["money"], idea_prompt)

    # Judge reads all 4 and gives the final verdict
    judge_prompt = f"""{idea_prompt}

MARKET ANALYST:
{market}

CUSTOMER:
{customer}

SKEPTIC:
{skeptic}

MONEY EXPERT:
{money}

Now give your final verdict."""
    verdict = _ask(agents["judge"], judge_prompt)

    result = {
        "idea": idea,
        "market": market,
        "customer": customer,
        "skeptic": skeptic,
        "money": money,
        "verdict": verdict,
        "score": _find_score(verdict),
    }
    _save(result)
    return result


def _find_score(verdict: str):
    """Pull the X/10 score out of the judge's verdict, if present."""
    m = re.search(r"(\d{1,2})\s*/\s*10", verdict)
    return int(m.group(1)) if m else None


def _save(result: dict) -> None:
    """Save the full review to a markdown file."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    slug = re.sub(r"[^\w]+", "_", result["idea"].lower()).strip("_")[:40]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    text = (f"# Startup Validation\n\n**Idea:** {result['idea']}\n\n"
            f"## Verdict\n{result['verdict']}\n\n"
            f"## Market\n{result['market']}\n\n## Customer\n{result['customer']}\n\n"
            f"## Risks\n{result['skeptic']}\n\n## Money\n{result['money']}\n")
    (OUTPUT_DIR / f"{slug}_{ts}.md").write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="AI Startup Idea Validator")
    parser.add_argument("--idea", default="An app that turns your old clothes into cash by matching them with local thrift buyers.")
    args = parser.parse_args()

    print_current_config()
    result = validate_idea(args.idea)
    print(f"\n===== VERDICT (score: {result['score']}) =====\n{result['verdict']}")
    for key in ("market", "customer", "skeptic", "money"):
        print(f"\n===== {key.upper()} =====\n{result[key]}")


if __name__ == "__main__":
    main()
