import os
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor
from pathlib import Path

# Load API key
load_dotenv()
# =========================
# LLM CONFIG (Groq)
# =========================
def get_config():
    return {
        "config_list": [
            {
                "model": "llama-3.1-8b-instant",
                "api_key": os.getenv("GROQ_API_KEY"),
                "api_type": "groq",
            }
        ],
        "temperature": 0.5,
    }

# =========================
# SETUP WORK DIRECTORY
# =========================
BASE_DIR = Path(__file__).parent
WORK_DIR = BASE_DIR / "workspace"
WORK_DIR.mkdir(exist_ok=True)    

executor =  LocalCommandLineCodeExecutor(
    work_dir= WORK_DIR,
    timeout =30
)

assistant = AssistantAgent(
    name="Coder",
    system_message="""
    You are a Python coder.
    Rules:
    - ONLY return Python code
    - Use ```python``` block
    - NO explanation
    - NO extra text

    End with DONE
    """,

    llm_config=get_config()
)

proxy = UserProxyAgent(
    name="Runner",
    human_input_mode="NEVER",
    code_execution_config={"executor": executor},
    is_termination_msg=lambda msg: "DONE" in (msg.get("content") or ""),
)


def main():
         # Start conversation
    proxy.initiate_chat(
        assistant,
        message="""
        Write Python code to:
        1. Find first 5 prime numbers
        2. Print their sum
        """,
            )

if __name__ == "__main__":
    main()