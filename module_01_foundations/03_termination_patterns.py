"""
module_01_foundations/03_termination_patterns.py
-------------------------------------------------
Five different ways to control when a conversation ends.

Proper termination is critical — bad termination means:
- Infinite loops (wasting API tokens)
- Conversations that stop too early
- Rate limit hits

Patterns covered:
1. Keyword-based (most common)
2. Max rounds (simplest)
3. Multi-keyword (flexible)
4. Content-length based
5. Structured output detection (JSON/markdown marker)

Run: python module_01_foundations/03_termination_patterns.py
"""
import os
import sys
import json

# Add project root to Python path so we can import config/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen import AssistantAgent, UserProxyAgent
from config.llm_config import get_llm_config
# ------------------------------------------------------------
# Helper function
# ------------------------------------------------------------
def run_pattern(pattern_name: str, user_proxy: UserProxyAgent, assistant: AssistantAgent, message: str) -> None:
    """Run a termination pattern demo with a clean header."""
    print(f"\n{'='*50}")
    print(f"Pattern: {pattern_name}")
    print("=" * 50)

    user_proxy.initiate_chat(
        recipient=assistant,
        message=message
    )

# ------------------------------------------------------------
# Pattern 1 — Keyword termination
# ------------------------------------------------------------
def pattern_1_keyword() -> None:

    llm_config = get_llm_config(temperature=0.5)

    assistant = AssistantAgent(
        name="KWAgent",
        system_message="Answer questions briefly. ALWAYS end your final answer with the word: TERMINATE",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: msg.get("content", "").strip().endswith("TERMINATE"),
        max_consecutive_auto_reply=1,
    )

    run_pattern(
        "1 - Single Keyword (TERMINATE)",
        user_proxy,
        assistant,
        "Name 2 Python built-in data structures."
    )

# ------------------------------------------------------------
# Pattern 2 — Max rounds
# ------------------------------------------------------------
def pattern_2_max_rounds() -> None:

    llm_config = get_llm_config(temperature=0.5)

    assistant = AssistantAgent(
        name="BriefAgent",
        system_message="Answer every question in exactly 2 sentences. No more.",
        llm_config=llm_config,
        max_consecutive_auto_reply=1,
    )

    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        max_consecutive_auto_reply=0,
    )
    run_pattern(
        "2 - Max Rounds (auto-stop after 1 exchange)",
        user_proxy,
        assistant,
        "What is a Python generator?"
    )
# ------------------------------------------------------------
# Pattern 3 — Multi-keyword termination
# ------------------------------------------------------------
def pattern_3_multi_keyword() -> None:

    llm_config = get_llm_config(temperature=0.5)

    STOP_WORDS = {"COMPLETE", "SKIP", "ERROR", "DONE"}

    assistant = AssistantAgent(
        name="FlexAgent",
        system_message="""Answer questions concisely.
        End with:
        - COMPLETE if you answered fully
        - SKIP if the question is outside your expertise
        - ERROR if you can't understand the question""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: any(
            word in msg.get("content", "").upper()
            for word in STOP_WORDS
        ),
        max_consecutive_auto_reply=1,
    )

    run_pattern(
        "3 - Multi-Keyword (COMPLETE/SKIP/ERROR/DONE)",
        user_proxy,
        assistant,
        "What is the time complexity of Python's list.sort()?"
    )

# ------------------------------------------------------------
# Pattern 4 — Content length termination
# ------------------------------------------------------------
def pattern_4_content_length() -> None:

    llm_config = get_llm_config(temperature=0.5)

    def is_long_enough(msg: dict) -> bool:
        content = msg.get("content", "")
        return len(content) > 120

    assistant = AssistantAgent(
        name="LengthAgent",
        system_message="Explain Python recursion in detail.",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=is_long_enough,
        max_consecutive_auto_reply=1,
    )

    run_pattern(
        "4 - Content Length (stop when response >120 chars)",
        user_proxy,
        assistant,
        "Explain recursion in Python."
    )
# ------------------------------------------------------------
# Pattern 5 — Structured output detection
# ------------------------------------------------------------
def pattern_5_structured_output() -> None:

    llm_config = get_llm_config(temperature=0.3)

    def is_valid_json_response(msg: dict) -> bool:
        content = msg.get("content", "")

        try:
            if "{" in content and "}" in content:
                start = content.index("{")
                end = content.rindex("}") + 1
                json.loads(content[start:end])
                return True
        except (json.JSONDecodeError, ValueError):
            pass

        return False

    assistant = AssistantAgent(
        name="StructuredAgent",
        system_message="""Extract information and return it as a JSON object.
        Format your entire response as valid JSON:
        {
        "topic": "...",
        "definition": "...",
        "example": "...",
        "complexity": "beginner|intermediate|advanced"
        }
        Return ONLY the JSON.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    user_proxy = UserProxyAgent(
        name="DataExtractor",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=is_valid_json_response,
        max_consecutive_auto_reply=1,
    )

    run_pattern(
        "5 - Structured Output (JSON detection)",
        user_proxy,
        assistant,
        "Extract information about Python list comprehensions."
    )
# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
if __name__ == "__main__":
    pattern_1_keyword()
    pattern_2_max_rounds()
    pattern_3_multi_keyword()
    pattern_4_content_length()
    pattern_5_structured_output()