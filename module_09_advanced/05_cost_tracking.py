"""
module_09_advanced/05_cost_tracking.py
---------------------------------------
Token usage and cost tracking for AutoGen agents.

Demonstrates:
1. Per-run cost estimation
2. Cumulative cost tracking across sessions
3. Budget enforcement (abort if cost exceeds limit)
4. Cost comparison across providers

Token pricing (approximate, may change):
  Groq Llama3-70b:    $0.59/M input, $0.79/M output (as of 2024)
  Gemini 1.5 Flash:   Free tier (then $0.075/M input)
  OpenRouter Free:    $0 (free models)

Run: python module_09_advanced/05_cost_tracking.py
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen import AssistantAgent, UserProxyAgent
from config.llm_config import get_llm_config
from config.providers import PROVIDERS


# ============================================================
# Token Pricing Database
# ============================================================

# Prices in USD per 1M tokens
TOKEN_PRICES = {
    "llama3-70b-8192": {"input": 0.59, "output": 0.79},
    "llama3-8b-8192":  {"input": 0.05, "output": 0.08},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro":   {"input": 3.50, "output": 10.50},
    # Free models
    "meta-llama/llama-3.1-8b-instruct:free": {"input": 0.0, "output": 0.0},
}

DEFAULT_PRICE = {"input": 1.0, "output": 2.0}  # Fallback estimate


def get_token_price(model: str) -> dict:
    """Returns price dict for a model (falls back to default)."""
    for model_key, prices in TOKEN_PRICES.items():
        if model_key in model:
            return prices
    return DEFAULT_PRICE


# ============================================================
# Cost Tracker
# ============================================================

@dataclass
class RunCost:
    """Tracks costs for a single agent run."""
    run_id: str
    model: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    conversation_turns: int = 0
    duration_seconds: float = 0.0

    def calculate_cost(self):
        """Estimates cost based on token counts and model pricing."""
        prices = get_token_price(self.model)
        self.estimated_cost_usd = (
            (self.prompt_tokens / 1_000_000) * prices["input"] +
            (self.completion_tokens / 1_000_000) * prices["output"]
        )

    def to_dict(self) -> dict:
        return asdict(self)


class SessionCostTracker:
    """
    Tracks costs across multiple agent runs in a session.
    Optionally enforces a budget limit.
    """

    HISTORY_FILE = Path(__file__).parent / "cost_history.json"

    def __init__(self, budget_usd: float = None, model: str = "llama3-70b-8192"):
        self.budget_usd = budget_usd
        self.model = model
        self.runs: list[RunCost] = []
        self.session_start = time.time()
        self.history = self._load_history()

    def _load_history(self) -> list:
        if self.HISTORY_FILE.exists():
            try:
                return json.loads(self.HISTORY_FILE.read_text())
            except (json.JSONDecodeError, KeyError):
                pass
        return []

    def _save_history(self):
        all_runs = self.history + [r.to_dict() for r in self.runs]
        # Keep last 100 runs
        all_runs = all_runs[-100:]
        self.HISTORY_FILE.write_text(json.dumps(all_runs, indent=2))

    def start_run(self, run_id: str = None) -> RunCost:
        """Creates and registers a new run cost tracker."""
        run_id = run_id or f"run_{len(self.runs)+1}_{datetime.now().strftime('%H%M%S')}"
        run = RunCost(run_id=run_id, model=self.model)
        return run

    def finish_run(self, run: RunCost, messages: list = None, duration: float = 0.0):
        """Records completed run and checks budget."""
        run.duration_seconds = round(duration, 2)
        run.conversation_turns = len(messages) if messages else 0

        # Estimate token usage from message lengths
        # (Real token count requires the API response — this is an estimate)
        if messages:
            total_chars = sum(len(m.get("content", "")) for m in messages)
            estimated_tokens = total_chars // 4  # ~4 chars per token
            run.prompt_tokens = int(estimated_tokens * 0.7)
            run.completion_tokens = int(estimated_tokens * 0.3)
            run.total_tokens = estimated_tokens

        run.calculate_cost()
        self.runs.append(run)
        self._save_history()

        print(f"\n  Run cost: ${run.estimated_cost_usd:.6f} "
              f"(~{run.total_tokens:,} tokens, {run.duration_seconds:.1f}s)")

        # Budget check
        if self.budget_usd and self.total_cost > self.budget_usd:
            print(f"\n  ⚠ BUDGET EXCEEDED: ${self.total_cost:.4f} > ${self.budget_usd:.4f}")
            raise RuntimeError(f"Budget limit of ${self.budget_usd:.4f} exceeded!")

        return run

    @property
    def total_cost(self) -> float:
        return sum(r.estimated_cost_usd for r in self.runs)

    @property
    def total_tokens(self) -> int:
        return sum(r.total_tokens for r in self.runs)

    def print_summary(self):
        """Prints a formatted cost summary."""
        print(f"\n{'='*55}")
        print("Session Cost Summary")
        print(f"{'='*55}")
        print(f"Model          : {self.model}")
        print(f"Runs completed : {len(self.runs)}")
        print(f"Total tokens   : {self.total_tokens:,} (estimated)")
        print(f"Total cost     : ${self.total_cost:.6f}")
        if self.budget_usd:
            remaining = self.budget_usd - self.total_cost
            pct = (self.total_cost / self.budget_usd) * 100
            print(f"Budget used    : {pct:.1f}% (${remaining:.6f} remaining)")

        if self.runs:
            avg_cost = self.total_cost / len(self.runs)
            avg_tokens = self.total_tokens / len(self.runs)
            print(f"\nPer-run average:")
            print(f"  Cost   : ${avg_cost:.6f}")
            print(f"  Tokens : {avg_tokens:.0f}")

    def print_historical_stats(self):
        """Prints stats across all historical runs."""
        all_runs = self.history + [r.to_dict() for r in self.runs]
        if not all_runs:
            print("No historical data yet.")
            return

        total_historical_cost = sum(r.get("estimated_cost_usd", 0) for r in all_runs)
        print(f"\nHistorical stats ({len(all_runs)} total runs): "
              f"${total_historical_cost:.4f} cumulative")


# ============================================================
# Demo
# ============================================================

def demo_cost_tracking():
    """Shows cost tracking across multiple agent conversations."""
    print("\n" + "="*55)
    print("Cost Tracking Demo")
    print("="*55)

    llm_config = get_llm_config(temperature=0.3)
    model = llm_config.get("config_list", [{}])[0].get("model", "unknown")

    # Set a $0.01 budget (very tight — educational)
    tracker = SessionCostTracker(budget_usd=0.01, model=model)

    print(f"Model: {model}")
    print(f"Budget: ${tracker.budget_usd:.4f}")
    print(f"Price estimate: ${get_token_price(model)['input']:.3f}/M input tokens\n")

    # Run 2 short conversations and track costs
    questions = [
        "In one sentence, what is AutoGen?",
        "In one sentence, what is a GroupChat?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n--- Run {i} ---")
        run = tracker.start_run(f"demo_run_{i}")
        start_time = time.time()

        assistant = AssistantAgent(
            name="CostAwareAgent",
            system_message="Answer in exactly one sentence. Then say: COST_DONE",
            llm_config=llm_config,
            max_consecutive_auto_reply=1,
        )
        user = UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=lambda msg: "COST_DONE" in msg.get("content", ""),
            max_consecutive_auto_reply=1,
        )

        try:
            result = user.initiate_chat(assistant, message=question)
            duration = time.time() - start_time
            messages = assistant.chat_messages.get(user, [])
            tracker.finish_run(run, messages=messages, duration=duration)
        except RuntimeError as e:
            print(f"  Budget enforcement: {e}")
            break

    tracker.print_summary()
    tracker.print_historical_stats()


def demo_cost_comparison():
    """Compares estimated costs across providers for the same task."""
    print("\n" + "="*55)
    print("Provider Cost Comparison (Estimated)")
    print("="*55)

    # Simulate a typical research report task
    # Assume: 3000 input tokens, 2000 output tokens
    simulated_input = 3000
    simulated_output = 2000

    print(f"\nTask: Research report (estimated {simulated_input} input + {simulated_output} output tokens)")
    print(f"\n{'Provider':<25} {'Model':<35} {'Est. Cost'}")
    print("-" * 75)

    provider_models = [
        ("Groq (fast)", "llama3-70b-8192"),
        ("Groq (mini)", "llama3-8b-8192"),
        ("Gemini Flash", "gemini-1.5-flash"),
        ("Gemini Pro", "gemini-1.5-pro"),
        ("OpenRouter Free", "meta-llama/llama-3.1-8b-instruct:free"),
    ]

    for provider_name, model in provider_models:
        prices = get_token_price(model)
        cost = (simulated_input / 1_000_000 * prices["input"] +
                simulated_output / 1_000_000 * prices["output"])
        cost_str = "FREE" if cost == 0 else f"${cost:.6f}"
        print(f"  {provider_name:<23} {model:<35} {cost_str}")

    print(f"\nTip: For development, use OpenRouter free models.")
    print("For production, Groq llama3-8b-8192 gives the best cost/quality ratio.")


if __name__ == "__main__":
    demo_cost_comparison()
    print("\n" + "-"*55 + "\n")
    demo_cost_tracking()
