"""
module_09_advanced/02_agent_with_state.py
------------------------------------------
Stateful agents that persist data across conversation turns.

Demonstrates:
1. In-memory state (session-level persistence)
2. File-based state (cross-session persistence)
3. State-aware decision making

Use case: A tutoring agent that remembers what the student
has learned and adapts its explanations accordingly.

Run: python module_09_advanced/02_agent_with_state.py
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen import ConversableAgent, AssistantAgent, UserProxyAgent
from config.llm_config import get_llm_config


STATE_FILE = Path(__file__).parent / "tutor_state.json"


# ============================================================
# Stateful Tutor Agent
# ============================================================

class AdaptiveTutorAgent(AssistantAgent):
    """
    A tutoring agent that tracks student progress across sessions.

    State tracks:
    - Topics covered (to avoid repetition)
    - Student's current level (adjusts explanation complexity)
    - Questions asked (to identify knowledge gaps)
    - Session count (for engagement messages)
    """

    def __init__(self, name: str, student_name: str, state_file: Path = None, **kwargs):
        self.student_name = student_name
        self.state_file = state_file or STATE_FILE
        self.state = self._load_state()

        # Build system message dynamically based on state
        system_message = self._build_system_message()
        kwargs["system_message"] = system_message

        super().__init__(name=name, **kwargs)

    def _load_state(self) -> dict:
        """Loads state from JSON file if it exists."""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                print(f"  Loaded existing state: {len(data.get('topics_covered', []))} topics covered")
                return data
            except (json.JSONDecodeError, KeyError):
                pass

        # Default initial state
        return {
            "student_name": self.student_name,
            "level": "beginner",  # beginner, intermediate, advanced
            "topics_covered": [],
            "questions_asked": [],
            "sessions_completed": 0,
            "created_at": datetime.now().isoformat(),
            "last_session": None,
        }

    def _save_state(self):
        """Persists current state to JSON file."""
        self.state["last_session"] = datetime.now().isoformat()
        self.state_file.write_text(json.dumps(self.state, indent=2))

    def _build_system_message(self) -> str:
        """Creates a personalized system message based on current state."""
        level = self.state["level"]
        topics = self.state["topics_covered"]
        sessions = self.state["sessions_completed"]
        student = self.student_name

        complexity_guide = {
            "beginner": "Use simple analogies, avoid jargon, explain every term",
            "intermediate": "Assume basic Python knowledge, can use technical terms",
            "advanced": "Peer-level explanations, discuss trade-offs and internals",
        }

        topics_context = ""
        if topics:
            topics_str = ", ".join(topics[-5:])  # Last 5 topics
            topics_context = f"\nTopics already covered (avoid repeating): {topics_str}"

        greeting = "Welcome back! 🎉" if sessions > 0 else f"Hello {student}, excited to start learning together!"

        return f"""You are an adaptive Python/AutoGen tutor for {student}.

{greeting}
Student Level: {complexity_guide[level]}
Session #{sessions + 1}{topics_context}

Your behavior:
1. Personalize responses using the student's name
2. Adjust complexity based on their level
3. Don't re-explain topics already covered
4. After each explanation, ask ONE clarifying question
5. When the student demonstrates mastery, say: "LEVEL_UP" to advance their level
6. End session responses with: TUTOR_DONE"""

    def record_topic(self, topic: str):
        """Records a covered topic in state."""
        if topic not in self.state["topics_covered"]:
            self.state["topics_covered"].append(topic)
            self._save_state()

    def advance_level(self):
        """Advances student's learning level."""
        levels = ["beginner", "intermediate", "advanced"]
        current_idx = levels.index(self.state["level"])
        if current_idx < len(levels) - 1:
            self.state["level"] = levels[current_idx + 1]
            print(f"\n  Student leveled up! Now: {self.state['level']}")
            self._save_state()

    def end_session(self):
        """Saves session completion to state."""
        self.state["sessions_completed"] += 1
        self._save_state()
        print(f"\n  Session {self.state['sessions_completed']} saved")
        print(f"  Topics covered total: {len(self.state['topics_covered'])}")
        print(f"  Current level: {self.state['level']}")

    def get_progress_summary(self) -> str:
        """Returns a human-readable progress summary."""
        return (
            f"Student: {self.student_name} | "
            f"Level: {self.state['level']} | "
            f"Topics: {len(self.state['topics_covered'])} | "
            f"Sessions: {self.state['sessions_completed']}"
        )


# ============================================================
# Demo
# ============================================================

def demo_stateful_tutor():
    """
    Demonstrates a stateful tutor that remembers student progress.
    Run this twice to see state persistence in action.
    """
    print("\n" + "="*60)
    print("Adaptive Tutor — Stateful Agent Demo")
    print("="*60)

    llm_config = get_llm_config(temperature=0.6)

    # Create the stateful tutor
    tutor = AdaptiveTutorAgent(
        name="AdaptiveTutor",
        student_name="Nidhi",
        llm_config=llm_config,
        max_consecutive_auto_reply=3,
    )

    print(f"\nProgress: {tutor.get_progress_summary()}")

    student = UserProxyAgent(
        name="Student",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "TUTOR_DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )

    print("\nStarting tutoring session...\n")

    student.initiate_chat(
        tutor,
        message="Can you explain what GroupChat is in AutoGen and when I'd use it?",
    )

    # Record the topic that was covered
    tutor.record_topic("GroupChat")
    tutor.end_session()

    print(f"\nFinal progress: {tutor.get_progress_summary()}")
    print(f"State file saved: {tutor.state_file}")
    print("\nTip: Run this script again to see state persistence — the tutor")
    print("will remember this was session #2 and won't re-explain GroupChat.")


if __name__ == "__main__":
    demo_stateful_tutor()
