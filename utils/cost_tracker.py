"""
utils/cost_tracker.py
---------------------
Token usage tracking for AutoGen conversations.

Free APIs have no financial cost, but tracking token usage
helps you understand when you'll hit rate limits.

Usage:
    from utils.cost_tracker import CostTracker

    tracker = CostTracker()

    # After a conversation
    tracker.record_from_agent(agent, provider="groq", model="llama3-70b-8192")
    tracker.print_summary()
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class UsageRecord:
    """Token usage record for a single agent conversation."""
    agent_name: str
    provider: str
    model: str
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    num_messages: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class CostTracker:
    """
    Tracks token usage across agent conversations.

    Token usage = rate limit usage. Free APIs limit tokens per minute,
    so tracking this helps avoid hitting limits in long pipelines.
    """

    def __init__(self, daily_token_budget: Optional[int] = None):
        """
        Args:
            daily_token_budget: Warn when total tokens exceed this value.
                                Useful for staying within free tier daily limits.
        """
        self.records: List[UsageRecord] = []
        self.daily_token_budget = daily_token_budget
        self.session_start = datetime.now()

    def record(
        self,
        agent_name: str,
        provider: str,
        model: str,
        total_tokens: int,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        num_messages: int = 0,
    ) -> UsageRecord:
        """Manually records token usage for an agent."""
        record = UsageRecord(
            agent_name=agent_name,
            provider=provider,
            model=model,
            total_tokens=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            num_messages=num_messages,
        )
        self.records.append(record)
        return record

    def record_from_agent(self, agent, provider: str, model: str) -> UsageRecord:
        """
        Attempts to extract token usage from an AutoGen agent's chat history.

        AutoGen 0.2 stores some usage data in agent chat messages.
        Note: Not all providers return token counts in their responses.
        """
        chat_history = getattr(agent, "chat_messages", {})
        total_tokens = 0
        num_messages = 0

        for _, messages in chat_history.items():
            for msg in messages:
                if isinstance(msg, dict):
                    usage = msg.get("usage", {})
                    if usage:
                        total_tokens += usage.get("total_tokens", 0)
                    num_messages += 1

        return self.record(
            agent_name=agent.name,
            provider=provider,
            model=model,
            total_tokens=total_tokens,
            num_messages=num_messages,
        )

    @property
    def total_tokens(self) -> int:
        """Sum of all tracked tokens across all agents."""
        return sum(r.total_tokens for r in self.records)

    def print_summary(self) -> None:
        """Prints a formatted token usage summary."""
        print()
        print("=" * 55)
        print("  TOKEN USAGE SUMMARY")
        print("=" * 55)
        print(f"  Session started: {self.session_start.strftime('%H:%M:%S')}")
        print()

        if not self.records:
            print("  No usage recorded. Call record() or record_from_agent().")
        else:
            for r in self.records:
                print(f"  Agent:    {r.agent_name}")
                print(f"  Provider: {r.provider} | Model: {r.model}")
                print(f"  Tokens:   {r.total_tokens:,} | Messages: {r.num_messages}")
                print()

            print("-" * 55)
            print(f"  TOTAL TOKENS: {self.total_tokens:,}")

            if self.daily_token_budget:
                pct = (self.total_tokens / self.daily_token_budget) * 100
                print(f"  DAILY BUDGET: {pct:.1f}% of {self.daily_token_budget:,}")

                if pct > 80:
                    print("  WARNING: Approaching daily token budget!")

        print("=" * 55)
        print()

    def to_dict(self) -> dict:
        """Serializes usage data to a dict for saving."""
        return {
            "session_start": self.session_start.isoformat(),
            "total_tokens": self.total_tokens,
            "records": [
                {
                    "agent": r.agent_name,
                    "provider": r.provider,
                    "model": r.model,
                    "tokens": r.total_tokens,
                    "messages": r.num_messages,
                    "timestamp": r.timestamp,
                }
                for r in self.records
            ],
        }

    def save(self, filepath: str = "usage_report.json") -> None:
        """Saves usage data as JSON."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Usage report saved: {filepath}")
