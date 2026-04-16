"""
This script demonstrates a safe code execution setup using AutoGen.

It creates two agents:
1. SafeCoder (AssistantAgent) → generates Python code
2. Runner (UserProxyAgent) → executes that code safely

Key features:
- Uses a restricted environment (workspace folder)
- Prevents unsafe operations (no OS/system calls, no network)
- Limits execution time to avoid infinite loops
- Ensures controlled and secure code execution

The task:
Generate random numbers, filter prime numbers,
and display the count and top 5 largest primes.
"""

import os
from pathlib import Path
from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv

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
        "temperature": 0,
    }


# ------------------ Setup ------------------

# Creating a folder named 'workspace'
WORK_DIR = Path("workspace")

# This will create the folder automatically if it doesn't exist
WORK_DIR.mkdir(exist_ok=True)

# local executor that run generated python code
executor =  LocalCommandLineCodeExecutor(
    work_dir= WORK_DIR,
    timeout =10 # prevent infine loops
)

SAFE_MSG = """
You are a safe Python coder.

Rules:
- Only standard library
- No network calls
- No subprocess, os.system
- No file access outside current directory
- No infinite loops
- Output ONLY ONE python code block
- DO NOT include SAFE_DONE anywhere in code
- SAFE_DONE is only a conversation-level signal, not code
"""

# write safe python codeS
coder = AssistantAgent(
    name="SafeCoder",
    system_message=SAFE_MSG,
    llm_config=get_config()
)

# =========================
# Runner agent , execute the generated code 
# =========================
runner = UserProxyAgent(
    name="Runner",
    human_input_mode="NEVER",
    code_execution_config={"executor": executor, "capture_output": True},
    max_consecutive_auto_reply=1,
    is_termination_msg=lambda msg: "SAFE_DONE" in (msg.get("content") or ""),
     
)
# entry poin of this script
if __name__ == "__main__":
    runner.initiate_chat(
        coder,
        message="""
Generate 100 random numbers (1–1000),
find primes,
print count and top 5 largest primes.
"""
    )
