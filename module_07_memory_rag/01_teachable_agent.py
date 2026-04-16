
# ============================================
# TEACHABLE AGENT 
# Persistent memory + AutoGen + GROQ
# ============================================

import os
from pathlib import Path
from dotenv import load_dotenv

from autogen import AssistantAgent, UserProxyAgent

load_dotenv()

# =========================
# LLM CONFIG (GROQ)
# =========================
def get_llm_config():
    return {
        "config_list": [
            {
                "model": "llama-3.1-8b-instant",
                "api_key": os.getenv("GROQ_API_KEY"),
                "api_type": "groq",
            }
        ],
        "temperature": 0.7,
    }



# =========================
# MEMORY SYSTEM (FILE BASED)
# =========================

BASE_DIR = Path(__file__).resolve().parent
MEMORY_DIR = BASE_DIR / "memory_db"
MEMORY_DIR.mkdir(exist_ok=True)
MEMORY_FILE = MEMORY_DIR / "memory_store.txt"


def load_memory():
    # Check if the memory file exists on disk
    if MEMORY_FILE.exists():
        # Read the entire file content as a string
        data = MEMORY_FILE.read_text(encoding="utf-8").strip()

        # If file is empty, return an empty list
        if not data:
            return []

        # Split file content by new lines to convert it into a list
        return data.split("\n")

    # If file does not exist, return empty memory
    return []


def save_memory(memories):
    # Convert list of memories into a single string separated by new lines
    # and write it into the memory file (overwrite mode)
    MEMORY_FILE.write_text("\n".join(memories), encoding="utf-8")   


def add_memory(text):
    # Load existing memories from file
    memories = load_memory()

    # Avoid duplicate entries in memory
    # (prevents storing same information multiple times)
    if text not in memories:
        memories.append(text)

    # Save updated memory list back to file
    save_memory(memories)

def get_memory_context():
    # Load all stored memories
    memories = load_memory()

    # If no memory exists, return a default message
    if not memories:
        return "No memories stored yet."

    # Format each memory as a bullet point string
    # Example:
    # - User name is Nidhi
    # - Likes bullet points
    return "\n".join(f"- {m}" for m in memories)    

# =========================
# BUILD AGENT
# =========================
def build_agent():
    llm_config = get_llm_config()

    return AssistantAgent(
        name="SmartAssistant",
        system_message=f"""
You are a helpful AI assistant with persistent memory.

USER MEMORY:
{get_memory_context()}

RULES:
- Always use memory if relevant
- If user gives new info, accept it
- Be concise
- End response with DONE
""",
        llm_config=llm_config,
    )


# =========================
# MAIN DEMO
# =========================
def run_demo():
    print("\n====================================")
    print(" TEACHABLE AGENT - FINAL VERSION ")
    print("====================================\n")

    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "DONE" in msg.get("content", ""),
    ) 

    # =========================
    # SESSION 1: TEACH
    # =========================
    print("\n--- Session 1: Teaching ---\n")

    add_memory("User name is Nidhi")
    add_memory("User is learning AutoGen")
    add_memory("User prefers bullet-point answers")   

    assistant = build_agent()

    user.initiate_chat(
        assistant,
    )

    # =========================
    # SESSION 2: TEST MEMORY
    # =========================
    print("\n--- Session 2: Testing Memory ---\n")

    assistant = build_agent()

    user.initiate_chat(
        assistant,
        message="What do you remember about me?",
    )

    print("\n💾 Memory saved at:", MEMORY_FILE)
    
# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_demo()