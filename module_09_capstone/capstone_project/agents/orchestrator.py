"""Orchestrator — runs the research stage (no LLM, just coordinates)."""

from autogen import UserProxyAgent


def create_orchestrator() -> UserProxyAgent:
    """Starts the research task and waits for the knowledge package."""
    return UserProxyAgent(
        name="Orchestrator",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "RESEARCH_PACKAGE_COMPLETE" in msg.get("content", ""),
        max_consecutive_auto_reply=2,
    )
