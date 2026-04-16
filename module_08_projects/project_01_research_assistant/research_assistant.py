"""
project_01_research_assistant/research_assistant.py
-----------------------------------------------------
Main entry point for the Research Assistant.

A 5-agent pipeline that researches any topic and produces a markdown report.
This is NOT a chatbot — it's a document generation pipeline.

Usage:
    python module_08_projects/project_01_research_assistant/research_assistant.py
    python module_08_projects/project_01_research_assistant/research_assistant.py --topic "quantum computing"
    python module_08_projects/project_01_research_assistant/research_assistant.py --provider groq

Architecture:
    Admin → GroupChatManager → [Orchestrator, Researcher, FactChecker, Analyst, Writer]
"""

import argparse
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from autogen import GroupChat, GroupChatManager
from config.llm_config import get_llm_config
from module_08_projects.project_01_research_assistant.agents import create_research_agents
from module_08_projects.project_01_research_assistant.tools import register_research_tools


def run_research_pipeline(topic: str, provider: str = None) -> str:
    """
    Runs the complete research pipeline for a topic.

    Args:
        topic: The research topic
        provider: LLM provider override (default: from .env)

    Returns:
        Final report content as string
    """
    print("\n" + "="*65)
    print("RESEARCH ASSISTANT — AutoGen 5-Agent Pipeline")
    print("="*65)
    print(f"Topic: {topic}")
    print()

    llm_config = get_llm_config(provider=provider, temperature=0.7)
    agents = create_research_agents(llm_config)

    # Register tools with the writer agent (it will save the report)
    register_research_tools(agents["writer"], agents["admin"])

    groupchat = GroupChat(
        agents=[
            agents["admin"],
            agents["orchestrator"],
            agents["researcher"],
            agents["fact_checker"],
            agents["analyst"],
            agents["writer"],
        ],
        messages=[],
        max_round=25,
        speaker_selection_method="auto",
    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: "REPORT_COMPLETE" in msg.get("content", ""),
    )

    agents["admin"].initiate_chat(
        manager,
        message=f"""Research Topic: {topic}

Pipeline:
1. Orchestrator: Break into 3-4 sub-questions and coordinate
2. Researcher: Answer each sub-question with factual depth
3. FactChecker: Verify key claims
4. Analyst: Identify patterns and insights
5. Writer: Create the final report and save it using save_report tool

Begin the research pipeline now.""",
    )

    # Find and return the last message from the writer
    for msg in reversed(groupchat.messages):
        if msg.get("name") == "ReportWriter":
            return msg.get("content", "")
    return "Research complete. Check output/ directory for the report."


def main():
    parser = argparse.ArgumentParser(description="AutoGen Research Assistant")
    parser.add_argument("--topic", default="The impact of large language models on software development",
                        help="Research topic")
    parser.add_argument("--provider", default=None,
                        choices=["groq", "gemini", "openrouter", "huggingface"])
    args = parser.parse_args()
    result = run_research_pipeline(args.topic, args.provider)
    print(f"\n{'='*65}\nReport generated. Check output/ directory.\n{'='*65}")


if __name__ == "__main__":
    main()
