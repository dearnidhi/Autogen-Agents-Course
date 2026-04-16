"""
module_09_advanced/04_logging_tracing.py
-----------------------------------------
Production logging and conversation tracing for AutoGen agents.

Demonstrates:
1. Structured logging with loguru
2. Conversation tracer (captures every turn)
3. Execution timeline with timing
4. Log file rotation and management

Run: python module_09_advanced/04_logging_tracing.py
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen import AssistantAgent, UserProxyAgent
from config.llm_config import get_llm_config


# ============================================================
# Setup Structured Logging
# ============================================================

LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

try:
    from loguru import logger

    # Remove default stderr sink
    logger.remove()

    # Console: Human-readable output
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | {message}",
        level="INFO",
        colorize=True,
    )

    # File: Structured JSON for analysis
    logger.add(
        LOGS_DIR / "autogen_{time:YYYY-MM-DD}.log",
        rotation="50 MB",
        retention="10 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
    )

    LOGURU_AVAILABLE = True
    logger.info("Loguru logging initialized")

except ImportError:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logger = logging.getLogger("autogen_course")
    LOGURU_AVAILABLE = False
    logger.info("Using standard library logging (install loguru for structured logging)")


# ============================================================
# Conversation Tracer
# ============================================================

class ConversationTracer:
    """
    Captures the complete conversation history with timing,
    speaker identification, and message statistics.
    """

    def __init__(self, session_name: str):
        self.session_name = session_name
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = time.time()
        self.turns = []
        self.metadata = {
            "session_name": session_name,
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
        }
        logger.info(f"Tracer initialized: {session_name} [{self.session_id}]")

    def record_turn(self, speaker: str, content: str, turn_type: str = "message"):
        """Records a single conversation turn."""
        elapsed = time.time() - self.start_time
        turn = {
            "turn": len(self.turns) + 1,
            "elapsed_seconds": round(elapsed, 2),
            "speaker": speaker,
            "type": turn_type,
            "word_count": len(content.split()),
            "content_preview": content[:100] + ("..." if len(content) > 100 else ""),
        }
        self.turns.append(turn)
        logger.debug(f"Turn {turn['turn']} | {speaker} ({turn['word_count']} words)")

    def record_from_messages(self, messages: list, agent_names: list = None):
        """Populates tracer from GroupChat messages list."""
        for i, msg in enumerate(messages):
            speaker = msg.get("name", msg.get("role", "unknown"))
            content = msg.get("content", "")
            self.record_turn(speaker, content)

    def get_stats(self) -> dict:
        """Returns summary statistics for the conversation."""
        if not self.turns:
            return {}

        speakers = {}
        for turn in self.turns:
            sp = turn["speaker"]
            if sp not in speakers:
                speakers[sp] = {"turns": 0, "total_words": 0}
            speakers[sp]["turns"] += 1
            speakers[sp]["total_words"] += turn["word_count"]

        total_elapsed = time.time() - self.start_time
        return {
            "session_id": self.session_id,
            "total_turns": len(self.turns),
            "total_elapsed_seconds": round(total_elapsed, 2),
            "total_words": sum(t["word_count"] for t in self.turns),
            "speakers": speakers,
        }

    def save_trace(self, output_dir: Path = None) -> Path:
        """Saves full conversation trace as JSON."""
        output_dir = output_dir or LOGS_DIR
        output_dir.mkdir(exist_ok=True)

        trace_data = {
            "metadata": self.metadata,
            "stats": self.get_stats(),
            "turns": self.turns,
        }

        filepath = output_dir / f"trace_{self.session_id}.json"
        filepath.write_text(json.dumps(trace_data, indent=2))
        logger.info(f"Trace saved: {filepath}")
        return filepath

    def print_timeline(self):
        """Prints a visual timeline of the conversation."""
        print(f"\n{'='*60}")
        print(f"Conversation Timeline: {self.session_name}")
        print(f"{'='*60}")
        for turn in self.turns:
            bar = "█" * min(20, turn["word_count"] // 10)
            print(f"  Turn {turn['turn']:2d} [{turn['elapsed_seconds']:5.1f}s] "
                  f"{turn['speaker']:<20} {bar} ({turn['word_count']} words)")

        stats = self.get_stats()
        print(f"\nTotal: {stats['total_turns']} turns | "
              f"{stats['total_elapsed_seconds']}s | "
              f"{stats['total_words']} words")

        print("\nSpeaker breakdown:")
        for speaker, info in stats.get("speakers", {}).items():
            print(f"  {speaker}: {info['turns']} turns, {info['total_words']} words")


# ============================================================
# Instrumented Agent Wrapper
# ============================================================

def instrument_agent(agent, tracer: ConversationTracer):
    """
    Wraps an agent's generate_reply to automatically log each turn.
    Non-invasive — doesn't modify the agent class.
    """
    original_generate_reply = agent.generate_reply

    def traced_generate_reply(messages=None, sender=None, **kwargs):
        start = time.time()
        reply = original_generate_reply(messages=messages, sender=sender, **kwargs)
        elapsed = time.time() - start

        if reply and isinstance(reply, str):
            tracer.record_turn(
                speaker=agent.name,
                content=reply,
                turn_type="llm_reply",
            )
            logger.debug(f"{agent.name} replied in {elapsed:.2f}s ({len(reply.split())} words)")

        return reply

    agent.generate_reply = traced_generate_reply
    logger.info(f"Instrumented agent: {agent.name}")
    return agent


# ============================================================
# Demo
# ============================================================

def demo_logged_conversation():
    """A fully traced and logged agent conversation."""
    print("\n" + "="*55)
    print("Logging & Tracing Demo")
    print("="*55)

    tracer = ConversationTracer("autogen_logging_demo")
    llm_config = get_llm_config(temperature=0.5)

    logger.info("Creating agents", session_id=tracer.session_id if LOGURU_AVAILABLE else "")

    assistant = AssistantAgent(
        name="LoggedAssistant",
        system_message="""You are a concise AutoGen expert.
        Answer in 2-3 short paragraphs maximum.
        End with: LOGGING_DEMO_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    # Instrument the assistant for automatic tracing
    instrument_agent(assistant, tracer)

    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "LOGGING_DEMO_DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )

    logger.info("Starting conversation")

    # Record the initial user message
    tracer.record_turn("User", "What makes GroupChat useful for production AI systems?", "user_message")

    user.initiate_chat(
        assistant,
        message="What makes GroupChat useful for production AI systems?",
    )

    logger.info("Conversation complete", turns=len(tracer.turns))

    # Print the timeline
    tracer.print_timeline()

    # Save the trace
    trace_file = tracer.save_trace()
    print(f"\nFull trace saved: {trace_file}")
    print(f"Log files in: {LOGS_DIR}")


if __name__ == "__main__":
    demo_logged_conversation()
