"""
project_01_research_assistant/tools.py
-----------------------------------------
Custom tools for the Research Assistant pipeline.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

OUTPUT_DIR = Path(__file__).parent / "output"


def save_report(
    content: Annotated[str, "Full markdown content of the research report"],
    filename: Annotated[str, "Base filename without extension"] = "research_report",
) -> str:
    """Saves a research report to the output directory."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = OUTPUT_DIR / f"{filename}_{timestamp}.md"
    filepath.write_text(content, encoding="utf-8")
    return f"Report saved: {filepath}"


def create_outline(
    topic: Annotated[str, "Research topic"],
    num_questions: Annotated[int, "Number of sub-questions (2-5)"] = 4,
) -> str:
    """Creates a structured research outline with sub-questions."""
    outline = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "sub_questions": [
            f"What is the current state of {topic}?",
            f"What are the main challenges and limitations in {topic}?",
            f"What are the key trends and innovations in {topic}?",
            f"What are the practical applications of {topic}?",
            f"Who are the key players and stakeholders in {topic}?",
        ][:num_questions],
    }
    return json.dumps(outline, indent=2)


def register_research_tools(caller_agent, executor_agent) -> None:
    """Registers all research tools with appropriate agents."""
    from autogen import register_function
    register_function(save_report, caller=caller_agent, executor=executor_agent,
                      name="save_report", description="Save the completed research report to a markdown file")
    register_function(create_outline, caller=caller_agent, executor=executor_agent,
                      name="create_outline", description="Create a structured research outline with sub-questions")
