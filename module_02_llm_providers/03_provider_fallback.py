"""
module_02_llm_providers/03_provider_fallback.py
------------------------------------------------

🎯 PURPOSE:
- Use multiple LLM providers together
- Automatically switch if one fails

💡 WHY IMPORTANT:
- Real-world systems NEVER rely on one API
- Makes system reliable (production-ready)
"""

# -----------------------------------------
# Basic Python imports
# -----------------------------------------
import os
import sys
from dotenv import load_dotenv

# Load .env file (VERY IMPORTANT)
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -----------------------------------------
# AutoGen imports
# -----------------------------------------
from autogen import AssistantAgent, UserProxyAgent

# ✅ CORRECT import (as per YOUR providers.py)
from config.providers import GROQ_MODELS, OPENROUTER_MODELS


# -----------------------------------------
# STEP 1: BUILD FALLBACK CONFIG
# -----------------------------------------
def build_fallback_config(temperature: float = 0.7) -> dict:
    """
    Creates a list of multiple providers.
    AutoGen will try them one by one if one fails.
    """

    config_list = []

    # -----------------------------------------
    # Provider 1: GROQ (PRIMARY)
    # -----------------------------------------
    groq_key = os.getenv("GROQ_API_KEY")

    if groq_key and not groq_key.endswith("_here"):
        config_list.extend([
            {
                "model": GROQ_MODELS["fast"],        # fast model
                "api_key": groq_key,
                "api_type": "groq",
            },
            {
                "model": GROQ_MODELS["versatile"],   # powerful model
                "api_key": groq_key,
                "api_type": "groq",
            },
        ])
        print("✅ Groq added (fast + versatile)")
    else:
        print("❌ Groq skipped (API key missing)")

    # -----------------------------------------
    # Provider 2: OPENROUTER (BACKUP)
    # -----------------------------------------
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    if openrouter_key and not openrouter_key.endswith("_here"):
        config_list.append({
            "model": OPENROUTER_MODELS["default"],
            "api_key": openrouter_key,
            "base_url": "https://openrouter.ai/api/v1",
        })
        print("✅ OpenRouter added (backup)")
    else:
        print("❌ OpenRouter skipped (API key missing)")

    # -----------------------------------------
    # ERROR if no provider
    # -----------------------------------------
    if not config_list:
        raise EnvironmentError("No provider configured! Add API keys in .env")

    print(f"\n🎯 Total providers configured: {len(config_list)}")

    return {
        "config_list": config_list,
        "temperature": temperature
    }


# -----------------------------------------
# STEP 2: DEMO FALLBACK
# -----------------------------------------
def demo_fallback():
    print("\n" + "=" * 55)
    print("🚀 MULTI-PROVIDER FALLBACK DEMO")
    print("=" * 55)

    llm_config = build_fallback_config()

    # Show provider order
    print("\n📋 Provider order:")
    for i, cfg in enumerate(llm_config["config_list"]):
        provider = cfg.get("api_type", "openrouter")
        model = cfg["model"]
        print(f"{i+1}. {model} ({provider})")

    print("\n⚡ AutoGen will try providers one by one if failure happens")

    # Assistant
    assistant = AssistantAgent(
        name="FallbackAgent",
        system_message="""
You are a smart AI using multiple providers.

1. First tell which provider and model you are using
2. Then explain what happens if rate limit occurs

End with: FALLBACK_DONE
""",
        llm_config=llm_config,
    )

    # User
    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        max_consecutive_auto_reply=1,
        is_termination_msg=lambda msg: "FALLBACK_DONE" in msg.get("content", ""),
    )

    # Start chat
    user.initiate_chat(
        assistant,
        message="""
        Which provider are you using right now?
        What happens if rate limit hits?
        Then say FALLBACK_DONE
        """,
    )
# -----------------------------------------
# MAIN
# -----------------------------------------
if __name__ == "__main__":
    demo_fallback()