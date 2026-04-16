
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from autogen import AssistantAgent, UserProxyAgent

# Load environment variables
load_dotenv()

# =========================
# LLM CONFIG (Groq only)
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
        "temperature": 0.7,
    }


# =========================
# MEMORY FILE
# =========================
MEMORY_FILE = Path(__file__).parent / "persistent_memory.json"

# =========================
# MEMORY STORE
# =========================
class SimpleMemoryStore:
    """JSON-based persistent memory"""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.memories = []
        self._load()

    def _load(self):
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.memories = json.load(f)
            except json.JSONDecodeError:
                self.memories = []

    
    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, indent=2)

    
    def remember(self, key: str, value: str, category: str = "general"):
        self.memories.append({
            "key": key,
            "value": value,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()   

    def recall(self, query: str, top_k: int = 3):
        query_words = set(query.lower().split())
        scored = []

        for mem in self.memories:
            words = set((mem["key"] + " " + mem["value"]).lower().split())
            score = len(query_words & words)
            scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [mem for score, mem in scored[:top_k] if score > 0]    

    def to_context_string(self, query: str) -> str:
        relevant = self.recall(query)

        if not relevant:
            return "No relevant memories."

        return "\n".join(
            f"- [{m['category']}] {m['key']}: {m['value']}"
            for m in relevant
        )

    def __len__(self):
        return len(self.memories)         

# =========================
# TERMINATION CHECK
# =========================
def safe_termination_msg(msg: Optional[Dict[str, Any]]) -> bool:
    if not isinstance(msg, dict):
        return False
    content = msg.get("content", "")
    return isinstance(content, str) and "MEMORY_DONE" in content

# =========================
# MAIN DEMO
# =========================
def demo_memory_agent():
    print("\n" + "=" * 60)
    print("Persistent Memory Agent (JSON-based)")
    print("=" * 60)

    memory = SimpleMemoryStore(MEMORY_FILE)

    # Seed memory (only first run)
    if len(memory) == 0:
        memory.remember("user_name", "Nidhi", "user_profile")
        memory.remember("skill_level", "intermediate Python developer", "user_profile")
        memory.remember("learning_goal", "building multi-agent AI systems with AutoGen", "user_profile")
        memory.remember("completed_module", "module_01_foundations", "progress")
        memory.remember("completed_module", "module_02_llm_providers", "progress")
        memory.remember("preferred_provider", "Groq (llama3-70b)", "preferences")

        print(f"✓ Seeded memory with {len(memory)} entries")

    llm_config = get_config()

    # Retrieve relevant memory
    relevant_memories = memory.to_context_string("learning autogen Python")

    print(f"\n📚 Total memories: {len(memory)}")
    print("📌 Relevant memories:")
    print(relevant_memories)
    print()    

    assistant = AssistantAgent(
            name="MemoryAgent",
            system_message=f"""
            You are a personalized AutoGen tutor.

            User memory:
            {relevant_memories}

            Instructions:
            - Personalize responses using memory
            - Adapt to user's skill level
            - Consider learning goals
            - Keep answers practical

            End with MEMORY_DONE
            """,
            llm_config=llm_config,
        )

    user = UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=safe_termination_msg,
            max_consecutive_auto_reply=1,
        )
    
    user.initiate_chat(
        assistant,
        message="What should I focus on next in my AutoGen learning journey?",
    )

    # Save new memory
    memory.remember(
        "last_session_topic",
        "asked about next learning steps",
        "session"
    )
    print(f"\n💾 Memory updated. Total: {len(memory)}")
    print(f"📁 File: {MEMORY_FILE}")


if __name__ == "__main__":
    demo_memory_agent()

