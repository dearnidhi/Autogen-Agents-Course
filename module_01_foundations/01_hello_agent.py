"""
module_01_foundations/01_hello_agent.py
---------------------------------------
Your first AutoGen agent conversation.

This script shows the minimal viable AutoGen setup:
- One AssistantAgent (the AI brain)
- One UserProxyAgent (the task submitter)
- A simple task → response → terminate loop

Concepts covered:
- get_llm_config() — reading provider config from .env
- AssistantAgent — LLM-powered agent with a role
- UserProxyAgent — automated task submitter
- is_termination_msg — how to end a conversation
- system_message — defining agent behavior

Run: python module_01_foundations/01_hello_agent.py
"""
import os
import sys

# Add project root to Python path so we can import config/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen import AssistantAgent, UserProxyAgent
from config.llm_config import get_llm_config, print_current_config


def run_hello_agent() -> None:

    # --- 1. Print current config ---
    print("AutoGen Course — Module 01: Hello Agent")
    print("-" * 45)
    print_current_config()
    print()

    # --- 2. Build LLM Configuration ---
    llm_config = get_llm_config(temperature=0.7, seed=42)

    # --- 3. Create the AssistantAgent ---
    assistant = AssistantAgent(
        name="PythonTutor",
        system_message="""You are a friendly Python programming tutor for beginners.

Explain code using this structure:

1. WHAT IT DOES
2. KEY CONCEPTS
3. BEGINNER TIP

Keep it under 200 words.
End the response with TERMINATE.
""",
        llm_config=llm_config,
        max_consecutive_auto_reply=3,
    )

    # --- 4. Create the UserProxyAgent ---
    user_proxy = UserProxyAgent(
        name="Learner",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: (
            "TERMINATE" in msg.get("content", "")
        ),
        max_consecutive_auto_reply=2,
    )

    # --- 5. Start the Conversation ---
    print("Starting conversation...\n")
    print("=" * 50)

    user_proxy.initiate_chat(
        recipient=assistant,
        message="""Please explain this Python code:

def greet_user(name: str, times: int = 1) -> str:
    return "\\n".join([f"Hello, {name}!" for _ in range(times)])

result = greet_user("World", times=3)
print(result)
""",
    )

    print("\n" + "=" * 50)
    print("Conversation completed")

# Run the script
if __name__ == "__main__":
    run_hello_agent()