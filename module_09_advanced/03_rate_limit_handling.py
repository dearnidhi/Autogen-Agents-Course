"""
module_09_advanced/03_rate_limit_handling.py
--------------------------------------------
Production-grade rate limit handling for AutoGen agents.

Techniques demonstrated:
1. Exponential backoff decorator
2. Request rate limiter (token bucket)
3. Provider fallback chain
4. Monitoring rate limit events

Real-world usage: wrap your agent calls with these utilities
to handle free-tier API limits gracefully.

Run: python module_09_advanced/03_rate_limit_handling.py
"""

import os
import sys
import time
import threading
from datetime import datetime
from functools import wraps
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen import AssistantAgent, UserProxyAgent
from config.llm_config import get_llm_config, get_config_list


# ============================================================
# 1. Exponential Backoff Decorator
# ============================================================

class RateLimitTracker:
    """Tracks rate limit events for monitoring."""
    def __init__(self):
        self.events = []

    def record(self, provider: str, attempt: int, delay: float):
        self.events.append({
            "time": datetime.now().isoformat(),
            "provider": provider,
            "attempt": attempt,
            "delay_seconds": delay,
        })

    def summary(self) -> str:
        if not self.events:
            return "No rate limit events recorded."
        lines = [f"Rate limit events ({len(self.events)} total):"]
        for ev in self.events:
            lines.append(f"  [{ev['time'][:19]}] {ev['provider']} — attempt {ev['attempt']}, waited {ev['delay_seconds']:.1f}s")
        return "\n".join(lines)


TRACKER = RateLimitTracker()


def exponential_backoff(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
    retry_on_keywords: list = None,
    provider_name: str = "unknown",
):
    """
    Decorator for exponential backoff on rate limit errors.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds (doubles each retry)
        max_delay: Cap on delay (prevents waiting too long)
        exceptions: Exception types to catch
        retry_on_keywords: Only retry if error message contains these keywords
        provider_name: For logging/tracking
    """
    if retry_on_keywords is None:
        retry_on_keywords = ["429", "rate limit", "quota", "too many requests", "overloaded"]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    error_msg = str(e).lower()
                    is_rate_limit = any(kw in error_msg for kw in retry_on_keywords)

                    if not is_rate_limit and attempt > 0:
                        # Non-rate-limit error — don't retry
                        raise

                    if attempt == max_retries - 1:
                        raise RuntimeError(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}. Last error: {e}"
                        ) from e

                    # Calculate delay with exponential backoff + jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = delay * 0.1  # 10% jitter to avoid thundering herd
                    actual_delay = delay + (time.time() % jitter)

                    TRACKER.record(provider_name, attempt + 1, actual_delay)
                    print(f"  ⚠ Rate limited ({provider_name}). Attempt {attempt+1}/{max_retries}. "
                          f"Waiting {actual_delay:.1f}s...")
                    time.sleep(actual_delay)
                    last_error = e

            raise last_error

        return wrapper
    return decorator


# ============================================================
# 2. Token Bucket Rate Limiter
# ============================================================

class TokenBucketRateLimiter:
    """
    Limits request rate using the token bucket algorithm.
    Useful for self-imposed rate limiting BEFORE hitting API limits.

    Example: Groq allows 30 RPM → set rate=0.5 (1 request per 2s)
    to safely stay within limits.
    """

    def __init__(self, rate: float, capacity: float = None):
        """
        Args:
            rate: Requests per second allowed (e.g. 0.5 = 1 req/2s)
            capacity: Max burst size (default: rate * 2)
        """
        self.rate = rate
        self.capacity = capacity or rate * 2
        self.tokens = self.capacity
        self.last_refill = time.time()
        self._lock = threading.Lock()

    def _refill(self):
        """Adds tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def acquire(self, timeout: float = 30.0) -> bool:
        """
        Waits for a token to become available.

        Returns:
            True if acquired, False if timeout exceeded
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                self._refill()
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return True
            # Wait a bit before retrying
            time.sleep(0.1)
        return False

    def call_with_limit(self, func, *args, **kwargs):
        """Wraps a function call with rate limiting."""
        if not self.acquire():
            raise TimeoutError("Rate limiter timeout — too many requests")
        return func(*args, **kwargs)


# ============================================================
# 3. Multi-Provider Fallback Demo
# ============================================================

def demo_provider_fallback():
    """
    Demonstrates automatic provider fallback when one API is unavailable.
    AutoGen's config_list handles this natively.
    """
    print("\n" + "="*55)
    print("Provider Fallback Chain Demo")
    print("="*55)

    # Build a fallback config list
    # AutoGen tries each config in order until one succeeds
    providers_to_try = ["groq", "openrouter", "gemini"]
    config_list = []

    for provider in providers_to_try:
        try:
            # get_config_list returns the raw config_list for a provider
            configs = get_config_list(provider)
            config_list.extend(configs)
            print(f"  ✓ Added {provider} to fallback chain")
        except ValueError as e:
            print(f"  ✗ {provider} not available: {e}")

    if not config_list:
        print("\nNo providers configured. Set up at least one API key in .env")
        return

    print(f"\nFallback chain has {len(config_list)} config(s)")
    print("AutoGen will try them in order...\n")

    llm_config = {
        "config_list": config_list,
        "temperature": 0.5,
        "timeout": 30,
    }

    agent = AssistantAgent(
        name="ResilientAgent",
        system_message="You are helpful. Answer concisely. End with: RESILIENT_DONE",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "RESILIENT_DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )

    user.initiate_chat(
        agent,
        message="What are the top 3 benefits of multi-provider fallback in AI systems?",
    )


# ============================================================
# 4. Rate Limiter Demo (no API calls needed)
# ============================================================

def demo_rate_limiter():
    """Shows the token bucket rate limiter in action."""
    print("\n" + "="*55)
    print("Token Bucket Rate Limiter Demo")
    print("="*55)

    # Simulate Groq: 30 RPM = 0.5 RPS
    groq_limiter = TokenBucketRateLimiter(rate=0.5)

    print("Simulating 5 API calls with 0.5 RPS rate limit (Groq-safe)...")
    print("Expected: calls spaced ~2 seconds apart\n")

    def mock_api_call(call_num: int) -> str:
        return f"API call #{call_num} succeeded"

    start = time.time()
    for i in range(1, 4):  # Just 3 calls to keep demo fast
        result = groq_limiter.call_with_limit(mock_api_call, i)
        elapsed = time.time() - start
        print(f"  {result} at {elapsed:.1f}s")

    print(f"\nTotal time: {time.time() - start:.1f}s (expected ~4s for 3 calls at 0.5 RPS)")


if __name__ == "__main__":
    demo_rate_limiter()
    print("\n" + "-"*55 + "\n")
    demo_provider_fallback()
    print("\n" + "-"*55)
    print(TRACKER.summary())
