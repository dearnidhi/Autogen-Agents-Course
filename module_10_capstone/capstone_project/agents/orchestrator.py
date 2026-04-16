"""
Orchestrator agent — controls the research pipeline.
Manages the research process and ensures quality before passing to content pipeline.
"""

from autogen import UserProxyAgent


def create_orchestrator() -> UserProxyAgent:
    """
    The Orchestrator acts as the research pipeline manager.
    Uses UserProxyAgent (no LLM) to stay in control of the pipeline.
    """
    return UserProxyAgent(
        name="Orchestrator",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "RESEARCH_PACKAGE_COMPLETE" in msg.get("content", ""),
        max_consecutive_auto_reply=2,
        system_message="""You are the research pipeline manager.
        Your job is to coordinate the Researcher and Analyst.
        You initiate the research task and wait for the knowledge package.""",
    )
