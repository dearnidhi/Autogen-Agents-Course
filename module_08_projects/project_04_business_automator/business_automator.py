"""
module_08_projects/project_04_business_automator/business_automator.py
-----------------------------------------------------------------------
AI Business Document Automator — Main Entry Point

Automates professional business writing using a 4-agent pipeline:
  TaskAnalyzer → DraftWriter → QualityReviewer → FinalEditor

Supports: emails, reports, meeting agendas, and project proposals.

Usage:
    # Use a built-in sample task
    python module_08_projects/project_04_business_automator/business_automator.py --task email
    python module_08_projects/project_04_business_automator/business_automator.py --task report
    python module_08_projects/project_04_business_automator/business_automator.py --task meeting
    python module_08_projects/project_04_business_automator/business_automator.py --task proposal

    # Use a custom task file
    python module_08_projects/project_04_business_automator/business_automator.py \\
        --file sample_tasks/email_draft_request.txt

    # Specify provider
    python module_08_projects/project_04_business_automator/business_automator.py \\
        --task report --provider groq
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from autogen import GroupChat, GroupChatManager
from config.llm_config import get_llm_config, print_current_config
from workflow_agents import build_agent_team
from tasks import BusinessTask, load_task, load_task_from_file, format_task_for_agents


OUTPUT_DIR = Path(__file__).parent / "output"


def save_output(task_type: str, content: str) -> Path:
    """Saves the final output to the output directory."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{task_type}_{timestamp}.md"
    filepath = OUTPUT_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    return filepath


def extract_final_output(messages: list) -> str:
    """Extracts the final polished output from the conversation."""
    for msg in reversed(messages):
        content = msg.get("content", "")
        if "## FINAL OUTPUT" in content:
            # Extract everything after the marker
            start = content.find("## FINAL OUTPUT")
            end = content.find("TASK_COMPLETE")
            if end > start:
                return content[start:end].strip()
            return content[start:].replace("TASK_COMPLETE", "").strip()
    return "Output not found in conversation."


def run_business_automator(task: BusinessTask, provider: str = None) -> str:
    """
    Runs the 4-agent business automation pipeline.

    Args:
        task: BusinessTask object with task details
        provider: Optional LLM provider override

    Returns:
        The final polished business document as a string
    """
    print("\n" + "=" * 65)
    print("AI Business Document Automator")
    print("=" * 65)
    print(f"Task Type    : {task.task_type.upper()}")
    print(f"Description  : {task.description[:70]}...")
    print(f"Requirements : {len(task.requirements)} items")
    print("=" * 65)
    print_current_config()

    # Build agent team
    agents = build_agent_team(provider=provider)
    admin = agents["admin"]
    analyzer = agents["analyzer"]
    writer = agents["writer"]
    reviewer = agents["reviewer"]
    editor = agents["editor"]

    llm_config = get_llm_config(provider=provider)

    # Set up GroupChat with the 4 specialist agents
    groupchat = GroupChat(
        agents=[admin, analyzer, writer, reviewer, editor],
        messages=[],
        max_round=10,
        speaker_selection_method="auto",  # LLM decides who speaks next
    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: "TASK_COMPLETE" in msg.get("content", ""),
    )

    # Format the task as a clear prompt for the agents
    task_prompt = format_task_for_agents(task)

    print(f"\nStarting automation pipeline...")
    print("Agents: TaskAnalyzer → DraftWriter → QualityReviewer → FinalEditor\n")

    # Launch the pipeline
    admin.initiate_chat(
        manager,
        message=f"""Please complete this business task using our 4-step pipeline.

{task_prompt}

Pipeline:
1. TaskAnalyzer: Analyze requirements and set success criteria
2. DraftWriter: Write the complete first draft
3. QualityReviewer: Review and approve or request one revision
4. FinalEditor: Polish and deliver the final output""",
    )

    # Extract and return the final output
    messages = groupchat.messages
    final_output = extract_final_output(messages)

    print("\n" + "=" * 65)
    print("AUTOMATION COMPLETE")
    print("=" * 65)

    # Save to file
    saved_path = save_output(task.task_type, final_output)
    print(f"Output saved: {saved_path}")

    return final_output


def run_demo(task_type: str = "email", provider: str = None) -> None:
    """Runs the automator with a built-in sample task."""
    task = load_task(task_type)
    result = run_business_automator(task, provider=provider)
    print(f"\n{'='*65}")
    print("FINAL DOCUMENT PREVIEW:")
    print(f"{'='*65}")
    print(result[:800] + ("..." if len(result) > 800 else ""))


def main():
    parser = argparse.ArgumentParser(
        description="AI Business Document Automator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Task types (--task):
  email     Draft professional business emails
  report    Generate structured business reports
  meeting   Create focused meeting agendas
  proposal  Write project or business proposals

Examples:
  python business_automator.py --task email
  python business_automator.py --task report --provider gemini
  python business_automator.py --file sample_tasks/email_draft_request.txt
        """,
    )
    parser.add_argument(
        "--task",
        choices=["email", "report", "meeting", "proposal"],
        default="email",
        help="Type of business document to generate",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to a custom task file (overrides --task)",
    )
    parser.add_argument(
        "--provider",
        choices=["groq", "gemini", "openrouter", "huggingface"],
        default=None,
        help="LLM provider (default: uses DEFAULT_PROVIDER from .env)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        default=True,
        help="Save output to file (default: True)",
    )

    args = parser.parse_args()

    if args.file:
        task = load_task_from_file(args.file)
    else:
        task = load_task(args.task)

    run_business_automator(task, provider=args.provider)


if __name__ == "__main__":
    main()
