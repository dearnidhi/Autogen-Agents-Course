"""
module_03_conversation_patterns/05_custom_reply_function.py
------------------------------------------------------------
Custom reply functions - for Groq + OpenRouter only!
"""

import os
import sys
from dotenv import load_dotenv  # 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Union, List, Dict, Any
from autogen import AssistantAgent, UserProxyAgent

# 👇 ADD THIS - Load .env file
load_dotenv()


# ============================================================
# STEP 2: LLM CONFIG (Groq + OpenRouter)
# ============================================================
def get_working_config(temperature: float = 0.7) -> dict:
    """
    Creates LLM config using available API keys.

    - Checks if GROQ or OPENROUTER keys exist
    - Adds available providers
    - Returns config for agents
    """

    config_list = []

    # Get API keys from environment
    groq_key = os.getenv("GROQ_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    print("\nChecking API keys...")

    # Add Groq (fast)
    if groq_key:
        config_list.append({
            "model": "llama-3.1-8b-instant",
            "api_key": groq_key,
            "api_type": "groq",
        })
        print("✓ Groq added")

    # Add OpenRouter (backup)
    if openrouter_key:
        config_list.append({
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "api_key": openrouter_key,
            "base_url": "https://openrouter.ai/api/v1",
        })
        print("✓ OpenRouter added")

    # If no keys found → error
    if not config_list:
        raise ValueError("No API keys found. Check your .env file.")

    return {
        "config_list": config_list,
        "temperature": temperature,
    }

# ============================================================
# DEMO 1: KEYWORD ROUTER
# ============================================================
def demo_keyword_router()->None:
    """this demo show how we can control the ai response"""

    print("\n===== DEMO 1: KEYWORD ROUTER =====")
    
    llm_config = get_working_config(temperature=0.6)

    QUICK_ANSWERS = {
        "python version": "Use Python 3.10 or above.",
        "install": "Run: pip install autogen-agentchat",
        "free api": "Use Groq for free and fast access.",
    }

    def smart_router_reply(
        recipient: AssistantAgent,
        messages: List[Dict],
        sender: UserProxyAgent,
        config: Optional[Any],
    ) -> Union[str, Dict, None]:

        last_msg = messages[-1].get("content", "").lower()

        # STEP 2A: Check keyword
        for keyword, answer in QUICK_ANSWERS.items():
            if keyword in last_msg:
                print(f"[Router] Keyword matched: {keyword}")
                return True, f"{answer}\n\nROUTED_DONE"

        # STEP 2B: fallback to LLM
        print("[Router] No match → using LLM")
        return False, None

    assistant = AssistantAgent(
        name="SmartRouter",
        system_message="Answer Python questions. End with ROUTED_DONE",
        llm_config=llm_config,
        max_consecutive_auto_reply=1,
    )

    assistant.register_reply(
        trigger=UserProxyAgent,
        reply_func=smart_router_reply,
        position=0,
    )

    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "ROUTED_DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )

    print("\n--- Test 1: Keyword Match ---")
    user_proxy.initiate_chat(
        assistant,
        message="Which python version should I install?",
        clear_history=True,
    )

    print("\n--- Test 2: No Match ---")
    user_proxy.initiate_chat(
        assistant,
        message="Explain python generators briefly",
        clear_history=True,
    )


# ============================================================
# DEMO 2: MESSAGE PREPROCESSING
# ============================================================

def demo_preprocessing_reply() -> None:
    """
    GOAL: Modify user message BEFORE it goes to AI.
    """
    print("\n===== DEMO 2: PREPROCESSING =====")
    
    llm_config = get_working_config(temperature=0.7)

    USER_PROFILE = {
        "name": "Nidhi",
        "level": "intermediate",
        "completed": ["module_01", "module_02"],
    }

    def inject_user_context(
        recipient: AssistantAgent,
        messages: List[Dict],
        sender: UserProxyAgent,
        config: Optional[Any],
    ) -> Union[bool, tuple]:

        if not messages:
            return False, None
        
        context = (
            f"[User:{USER_PROFILE['name']},"
            f"Level:{USER_PROFILE['level']}]"
        )

        last_msg = messages[-1].copy()
        original = last_msg.get("content", "")

        last_msg["content"] = f"{context}\n\n{original}"
        messages[-1] = last_msg

        print("\n[Modified Message]:\n", last_msg["content"])


        return False, None

    tutor = AssistantAgent(
        name="Tutor",
        system_message="""
        Teach based on user's level.
        Give short explanation (3-4 lines only).
        No long examples.
        Do not mention context.
        End with TUTOR_DONE
        """,        
        llm_config=llm_config,
        max_consecutive_auto_reply=1,
    )

    tutor.register_reply(
        trigger=UserProxyAgent,
        reply_func=inject_user_context,
        position=0,
    )

    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "TUTOR_DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )
    
    user_proxy.initiate_chat(
        tutor,
        message="Explain Python async/await simply in 3 lines only.",
    )
# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":

    # Run keyword router demo
    #demo_keyword_router()

    # Uncomment to run second demo
    demo_preprocessing_reply()    



 

      