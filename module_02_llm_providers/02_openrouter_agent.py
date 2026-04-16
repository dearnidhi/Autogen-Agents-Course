"""
module_02_llm_providers/02_openrouter_agent.py
-------------------------------------------------
🎯 PURPOSE:
- Connect AutoGen with OpenRouter (FREE LLM provider)
- Verify API key manually before using AutoGen
- Show how real API requests work

💡 WHY THIS FILE:
In Module 1 → config was hidden (black box)
In Module 2 → we build everything manually (full control)
"""
# -----------------------------------------
# Basic Python imports
# -----------------------------------------
import os   # Used to read environment variables (API keys)
import sys  # Used to modify Python path
from dotenv import load_dotenv  # Loads .env file
# Load .env file (VERY IMPORTANT)
load_dotenv()

# Add project root so we can import config/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -----------------------------------------
# AutoGen imports
# -----------------------------------------
from autogen import AssistantAgent, UserProxyAgent
# AssistantAgent → AI brain
# UserProxyAgent → sends tasks automatically

# -----------------------------------------
# STEP 1: BUILD OPENROUTER CONFIG
# -----------------------------------------
def build_openrouter_config(
    model: str = "openai/gpt-3.5-turbo",
    temperature: float = 0.7
) -> dict:

    # Get API key from .env file
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "OPENROUTER_API_KEY not configured.\n"
            "Set OPENROUTER_API_KEY=sk-... in your .env file"
        )

    print(f"\n🔥 Using OpenRouter model: {model}")
    print("📡 Endpoint: https://openrouter.ai/api/v1")

    # Build config_list (CORE CONCEPT)
    return {
        "config_list": [
            {
                "model": model,
                "api_key": api_key,
                "base_url": "https://openrouter.ai/api/v1",
                "price": [0, 0],  # FREE models
            }
        ],
        "temperature": temperature,
    }
# -----------------------------------------
# STEP 2: OPENROUTER DEMO (AGENT)
# -----------------------------------------
def demo_openrouter():
    print("\n" + "=" * 55)
    print("🚀 OpenRouter Working Demo")
    print("=" * 55)
    # Build config (THIS GIVES BRAIN TO AGENT)
    llm_config = build_openrouter_config(
        model="openai/gpt-3.5-turbo",
        temperature=0.7
    )

    # Create Assistant (AI)
    assistant = AssistantAgent(
        name="Assistant",
        system_message="""
        You are a helpful assistant.
        Answer in one sentence.
        When done, say TASK_COMPLETE
        """,
        llm_config=llm_config,
    )
    # Create User Proxy
    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",  # Fully automatic
        code_execution_config=False,
        max_consecutive_auto_reply=1,
        is_termination_msg=lambda x: "TASK_COMPLETE" in (x.get("content", "") or ""),
    )
    # Start conversation
    user.initiate_chat(
        assistant,
        message="What is Python in one sentence? Then say TASK_COMPLETE",
    )
    print("\n✅ Demo complete.")
# -----------------------------------------
# STEP 3: QUICK API TEST (NO AUTOGEN)
# -----------------------------------------
def test_simple():
    import requests
    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ API key missing")
        return False
    # Headers = authentication
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Request data (what we ask AI)
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Say 'OpenRouter is working!'"}
        ],
        "max_tokens": 20
    }

    print("\n📡 Quick API test...")

    # Send request to OpenRouter
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )
    # SUCCESS
    if response.status_code == 200:
        result = response.json()
        # Extract AI response
        print(f"✅ {result['choices'][0]['message']['content']}")
        return True
    # ERROR
    else:
        print(f"❌ {response.status_code}: {response.text}")
        return False
# -----------------------------------------
# MAIN
# -----------------------------------------
if __name__ == "__main__":
    # Step 0: Verify API before using AutoGen
    if test_simple():
        print("\n🎉 OpenRouter working! Now running AutoGen demo...")
        demo_openrouter()
    else:
        print("\n❌ OpenRouter test failed. Check API key.")

        