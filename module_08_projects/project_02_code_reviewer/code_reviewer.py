"""
project_02_code_reviewer/code_reviewer.py
------------------------------------------
Main entry point for the AI Code Reviewer.

4-specialist review panel + summarizer for comprehensive Python code review.

Usage:
    python module_08_projects/project_02_code_reviewer/code_reviewer.py
    python module_08_projects/project_02_code_reviewer/code_reviewer.py --file path/to/your_code.py
    python module_08_projects/project_02_code_reviewer/code_reviewer.py --file module_08_projects/project_02_code_reviewer/sample_code/buggy_script.py
"""

import argparse
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from autogen import GroupChat, GroupChatManager
from config.llm_config import get_llm_config
from module_08_projects.project_02_code_reviewer.review_agents import create_review_agents
from utils.helpers import truncate_for_context


def review_code_file(filepath: str, provider: str = None) -> None:
    """Runs a full code review on a Python file."""
    code = Path(filepath).read_text(encoding="utf-8")
    review_code_string(code, filename=Path(filepath).name, provider=provider)


def review_code_string(code: str, filename: str = "code.py", provider: str = None) -> None:
    """Runs a full code review on a code string."""
    print("\n" + "="*65)
    print("AI CODE REVIEWER — 4-Specialist Panel + Summarizer")
    print("="*65)
    print(f"Reviewing: {filename} ({len(code)} chars)")
    print()

    llm_config = get_llm_config(provider=provider, temperature=0.4)
    agents = create_review_agents(llm_config)

    # Truncate for context limits
    code_for_review = truncate_for_context(code, max_chars=5000, label="Code")

    groupchat = GroupChat(
        agents=[
            agents["admin"],
            agents["syntax"],
            agents["security"],
            agents["style"],
            agents["performance"],
            agents["summarizer"],
        ],
        messages=[],
        max_round=14,
        speaker_selection_method="round_robin",  # Each reviewer takes a turn
    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: "REVIEW_COMPLETE" in msg.get("content", ""),
    )

    agents["admin"].initiate_chat(
        manager,
        message=f"""Please review this Python code:

```python
{code_for_review}
```

File: {filename}

Reviewers: Each specialist reviews from their domain, then Summarizer provides final verdict.""",
    )


def main():
    parser = argparse.ArgumentParser(description="AI Code Reviewer")
    parser.add_argument("--file", default=None, help="Python file to review")
    parser.add_argument("--provider", default=None, choices=["groq", "gemini", "openrouter", "huggingface"])
    args = parser.parse_args()

    if args.file:
        review_code_file(args.file, args.provider)
    else:
        # Demo with the sample buggy script
        sample = Path(__file__).parent / "sample_code" / "buggy_script.py"
        review_code_file(str(sample), args.provider)


if __name__ == "__main__":
    main()
