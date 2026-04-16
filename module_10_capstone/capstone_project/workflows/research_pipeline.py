"""
Research Pipeline — Stage 1 of the AI Content Factory.

Takes a topic and produces a structured knowledge package
that the content pipeline uses to write all 4 content pieces.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from autogen import GroupChat, GroupChatManager
from config.llm_config import get_llm_config
from ..agents.orchestrator import create_orchestrator
from ..agents.researcher import create_researcher
from ..agents.analyst import create_analyst
from ..agents.publisher import extract_knowledge_package


def run_research_pipeline(topic: str, provider: str = None) -> str:
    """
    Runs the research pipeline for a given topic.

    Args:
        topic: The topic to research
        provider: Optional LLM provider override

    Returns:
        knowledge_package: Structured text package for content writers
    """
    print("\n" + "=" * 60)
    print("Stage 1: Research Pipeline")
    print(f"Topic: {topic}")
    print("=" * 60)

    llm_config = get_llm_config(provider=provider, temperature=0.4)

    # Create research agents
    orchestrator = create_orchestrator()
    researcher = create_researcher(llm_config)
    analyst = create_analyst(llm_config)

    # Set up research GroupChat
    groupchat = GroupChat(
        agents=[orchestrator, researcher, analyst],
        messages=[],
        max_round=6,
        speaker_selection_method="round_robin",  # Orchestrator → Researcher → Analyst
    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: "RESEARCH_PACKAGE_COMPLETE" in msg.get("content", ""),
    )

    print("\nRunning: Orchestrator → Researcher → Analyst\n")

    orchestrator.initiate_chat(
        manager,
        message=f"""Research this topic comprehensively for a content marketing campaign:

TOPIC: {topic}

Researcher: Please gather comprehensive facts, statistics, expert angles, and unique insights.
Analyst: After Researcher completes, produce a structured knowledge package for content writers.""",
    )

    # Extract the knowledge package from conversation
    knowledge_package = extract_knowledge_package(groupchat.messages)

    if knowledge_package:
        print(f"\n✓ Knowledge package created ({len(knowledge_package.split())} words)")
    else:
        # Fallback: use the last analyst message
        for msg in reversed(groupchat.messages):
            if msg.get("name") == "Analyst":
                knowledge_package = msg.get("content", "")
                break
        print("\n⚠ Using fallback knowledge package (no structured markers found)")

    return knowledge_package
