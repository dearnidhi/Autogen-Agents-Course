"""
module_02_llm_providers/01_groq_agent.py
-----------------------------------------

🎯 PURPOSE OF THIS FILE:
Connect AutoGen agents with a REAL LLM provider (Groq).

Module 1:
- Used get_llm_config() → hidden logic (black box)

Module 2:
- Build config manually → FULL CONTROL

💡 WHY THIS IS IMPORTANT:
- Understand APIs
- Control models
- Debug easily
- Build real-world AI systems
"""

# -----------------------------------------
# Basic Python imports
# -----------------------------------------
import os   # Used to read environment variables (API keys)
import sys  # Used to modify Python path
from dotenv import load_dotenv  # ✅ ADD THIS

# Load .env file
load_dotenv() 

# Add project root so we can import config/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -----------------------------------------
# AutoGen imports
# -----------------------------------------
from autogen import AssistantAgent, UserProxyAgent
# AssistantAgent → AI brain
# UserProxyAgent → sends tasks automatically

from config.providers import GROQ_MODELS
# Dictionary of available Groq models


# -----------------------------------------
# STEP 1: Build Groq Configuration
# -----------------------------------------
def build_groq_config(
    model_key: str = "default",
    temperature: float = 0.7,
) -> dict:

    # Get API key from .env file
    api_key = os.getenv("GROQ_API_KEY")

    # Validate API key
    if not api_key or api_key.endswith("_here"):
        raise EnvironmentError(
            "GROQ_API_KEY not configured.\n"
            "Get free API key from https://console.groq.com\n"
            "Then set GROQ_API_KEY=gsk_... in your .env file"
        )

    # Select model from dictionary
    model = GROQ_MODELS.get(model_key, GROQ_MODELS["default"])
    print(f"Using Groq model: {model}")

    # Build config_list (CORE CONCEPT)
    return {
        "config_list": [
            {
                "model": model,        # Model name
                "api_key": api_key,    # API key
                "api_type": "groq",    # REQUIRED for Groq
            }
        ],
        "temperature": temperature,  # Controls randomness
        "seed": 42                   # Same output every run (for learning)
    }


# -----------------------------------------
# STEP 2: Basic Groq Agent Demo
# -----------------------------------------
def demo_basic_groq_agent() -> None:

    print("\n" + "=" * 55)
    print("Groq Demo 1: Basic Agent")
    print("=" * 55)

    # Build config
    llm_config = build_groq_config("default", temperature=0.7)

    # Create Assistant (AI)
    assistant = AssistantAgent(
        name="GroqAssistant",
        system_message="""You are a helpful Python tutor powered by Groq.
Give concise, practical answers.
End with: DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    # Create User Proxy
    user_proxy = UserProxyAgent(
        name="Student",
        human_input_mode="NEVER",  # Fully automatic
        code_execution_config=False,
        is_termination_msg=lambda msg: "DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )

    # Start conversation
    user_proxy.initiate_chat(
        assistant,
        message="Explain Python's *args and **kwargs in 3 bullet points."
    )


# -----------------------------------------
# STEP 3: Model Comparison Demo
# -----------------------------------------
def demo_groq_model_comparison() -> None:

    print("\n" + "=" * 55)
    print("Groq Demo 2: Model Comparison")
    print("=" * 55)

    task = "In one sentence, what is the main advantage of Python generators over lists?"

    models_to_test = ["fast", "versatile"]  

    for model_key in models_to_test:

        model_name = GROQ_MODELS[model_key]
        print(f"\n--- Model: {model_name} ---")

        api_key = os.getenv("GROQ_API_KEY", "")

        # Build config
        llm_config = {
            "config_list": [
                {
                    "model": model_name,  
                    "api_key": api_key,
                    "api_type": "groq",
                }
            ],
            "temperature": 0.3,
        }

        assistant = AssistantAgent(
            name=f"Agent_{model_key}",
            llm_config=llm_config,
            system_message="Answer in exactly one sentence.",
            max_consecutive_auto_reply=1,
        )

        user_proxy = UserProxyAgent(
            name="Tester",
            human_input_mode="NEVER",
            code_execution_config=False,
            max_consecutive_auto_reply=0,
        )

        user_proxy.initiate_chat(assistant, message=task)


# -----------------------------------------
# STEP 4: Code Generation Demo
# -----------------------------------------
def demo_groq_code_generation() -> None:

    print("\n" + "=" * 55)
    print("Groq Demo 3: Code Generation")
    print("=" * 55)

    llm_config = build_groq_config("mixtral", temperature=0.2)

    coder = AssistantAgent(
        name="GroqCoder",
        system_message="""You are an expert Python developer.
Write clean, well-commented Python code with type hints.
Include a brief docstring and a usage example.
End your response with: CODE_COMPLETE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=1,
    )

    user_proxy = UserProxyAgent(
        name="Developer",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: msg.get("content", "").strip().endswith("CODE_COMPLETE"),
        max_consecutive_auto_reply=1,
    )

    user_proxy.initiate_chat(
        coder,
        message="Write a Python function to read a CSV file and return top N rows based on a column."
    )

# -----------------------------------------
# MAIN ENTRY POINT
# -----------------------------------------
if __name__ == "__main__":
    # demo_basic_groq_agent()

    # # Uncomment to test more
    # demo_groq_model_comparison()
    demo_groq_code_generation()