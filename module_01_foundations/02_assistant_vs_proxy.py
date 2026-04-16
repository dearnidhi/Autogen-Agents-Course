"""
module_01_foundations/02_assistant_vs_proxy.py
----------------------------------------------
Deep dive: AssistantAgent vs UserProxyAgent differences.

Key concepts covered:
- human_input_mode: NEVER | TERMINATE | ALWAYS
- code_execution_config: enabling/disabling code execution
- Giving UserProxyAgent its own LLM (bidirectional intelligence)
- Difference between "brain" agents and "executor" agents

Run: python module_01_foundations/02_assistant_vs_proxy.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen import AssistantAgent, UserProxyAgent
from config.llm_config import get_llm_config


def demo_never_mode() -> None:
    """
    Demo 1: human_input_mode="NEVER"

    In this mode the UserProxyAgent NEVER waits for human input.
    The entire conversation runs automatically.

    Flow:
    UserProxyAgent -> sends task
    AssistantAgent -> generates answer
    UserProxyAgent -> checks termination rule
    Conversation stops
    """

    print("\n" + "=" * 55)
    print("DEMO 1: human_input_mode='NEVER' (fully automated)")
    print("=" * 55)

    llm_config = get_llm_config(temperature=0.5)

    expert = AssistantAgent(
        name="PythonExpert",
        system_message="""You are a Python expert.
Answer questions concisely in 3-5 sentences.
End with: DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    auto_user = UserProxyAgent(
        name="AutoUser",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )

    # Start conversation
    auto_user.initiate_chat(
        expert,
        message="What is the difference between a list and a tuple in Python? Be brief.",
    )


def demo_terminate_mode() -> None:
    """
    Demo 2: human_input_mode="TERMINATE"

    The conversation runs automatically, but before the final
    termination the system pauses and asks for human input.

    This allows a human to review the final response.
    """

    print("\n" + "=" * 55)
    print("DEMO 2: human_input_mode='TERMINATE' (supervised)")
    print("=" * 55)

    print("(This demo will ask for input before terminating — just press Enter)")
    print()

    llm_config = get_llm_config(temperature=0.5)

    assistant = AssistantAgent(
        name="Advisor",
        system_message="""Give a practical tip about Python best practices.
Keep it to 2-3 sentences. End with: RECOMMENDATION_COMPLETE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    supervised_user = UserProxyAgent(
        name="Manager",
        human_input_mode="TERMINATE",
        code_execution_config=False,
        is_termination_msg=lambda msg: "RECOMMENDATION_COMPLETE" in msg.get(
            "content", ""
        ),
        max_consecutive_auto_reply=2,
    )

    supervised_user.initiate_chat(
        assistant,
        message="Give me one Python best practice for writing clean functions.",
    )


def demo_proxy_with_llm() -> None:
    """
    Demo 3: UserProxyAgent WITH its own LLM

    Normally the UserProxyAgent only manages conversation flow.
    But if we provide an llm_config, it becomes intelligent.

    Now BOTH agents generate messages.

    Result: AI-to-AI conversation.
    """

    print("\n" + "=" * 55)
    print("DEMO 3: Proxy with LLM (both agents think!)")
    print("=" * 55)

    llm_config = get_llm_config(temperature=0.5)

    python_expert = AssistantAgent(
        name="Expert",
        system_message="""You are a Python expert.
Answer questions clearly and add one practical example.
When you feel the topic is fully covered, end with: FINAL_ANSWER""",
        llm_config=llm_config,
        max_consecutive_auto_reply=3,
    )

    smart_questioner = UserProxyAgent(
        name="CuriousLearner",
        human_input_mode="NEVER",
        code_execution_config=False,
        llm_config=llm_config,
        system_message="""You are a curious student learning Python.
After each answer, ask ONE specific follow-up question.
Focus on practical applications.
When the expert says FINAL_ANSWER, respond with just: UNDERSTOOD""",
        is_termination_msg=lambda msg: "FINAL_ANSWER" in msg.get("content", ""),
        max_consecutive_auto_reply=3,
    )

    smart_questioner.initiate_chat(
        python_expert,
        message="Can you explain Python decorators and why they're useful?",
    )


if __name__ == "__main__":
    # Run Demo 1
    #demo_never_mode()

    # Run Demo 2 (requires pressing Enter)
    #demo_terminate_mode()

    # Run Demo 3 (AI ↔ AI conversation)
    demo_proxy_with_llm()