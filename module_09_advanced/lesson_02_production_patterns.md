# Lesson 02: Production Patterns

## The Gap Between Demo and Production

A demo agent that works in a Jupyter notebook often fails in production because:
- APIs have rate limits (429 errors)
- LLM responses are non-deterministic (outputs vary)
- Tokens cost money (costs grow unexpectedly)
- Conversations have no observability (debugging is blind)
- Multi-user scenarios cause conflicts (shared state)

This module addresses each of these.

---

## 1. Rate Limit Handling

### The Problem
Free APIs have strict limits:
| Provider | Rate Limit |
|----------|-----------|
| Groq | 30 RPM, 14,400 TPM |
| Gemini | 15 RPM, 1,500 RPD |
| OpenRouter | varies by model |
| HuggingFace | Serverless inference queue |

### The Solution: Exponential Backoff

```python
import time
import httpx
from functools import wraps

def retry_with_backoff(max_retries=5, base_delay=1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e) or "rate limit" in str(e).lower():
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limited. Waiting {delay:.1f}s (attempt {attempt+1})")
                        time.sleep(delay)
                    else:
                        raise
            raise RuntimeError(f"Max retries ({max_retries}) exceeded")
        return wrapper
    return decorator
```

---

## 2. Cost Tracking

### Why It Matters
A GroupChat with 5 agents and 10 rounds can easily use 50,000+ tokens.
At $5/M tokens, that's $0.25 per run. 1000 users = $250.

### Track Tokens Per Run

```python
def extract_token_usage(chat_result) -> dict:
    """Extracts token usage from an AutoGen ChatResult."""
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    if hasattr(chat_result, "cost"):
        cost_info = chat_result.cost
        if isinstance(cost_info, dict):
            for key, val in cost_info.items():
                if isinstance(val, dict):
                    usage["total_tokens"] += val.get("total_tokens", 0)
    return usage
```

---

## 3. Structured Logging

### What to Log (and What NOT to)

**Log:**
- Agent names and turn counts
- Token usage per conversation
- Errors and retries
- Execution time
- Final output (truncated)

**Don't log:**
- Full conversation history (verbose)
- API keys (obvious)
- User PII in production
- Every intermediate LLM response

### Loguru Example

```python
from loguru import logger

logger.add(
    "logs/autogen_{time}.log",
    rotation="50 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
)

logger.info("Starting research pipeline", topic=topic, provider=provider)
logger.warning("Rate limit hit, retrying", attempt=3, delay=4.0)
logger.error("Pipeline failed", error=str(e))
```

---

## 4. Configuration Management

### Never Hardcode Settings

```python
# BAD
llm_config = {"model": "llama3-70b-8192", "api_key": "gsk_abc123"}

# GOOD
from config.llm_config import get_llm_config
llm_config = get_llm_config()  # Reads from environment
```

### Environment Hierarchy

```
.env.local          # Developer-specific (never commit)
.env                # Project defaults (never commit)
.env.example        # Template (commit this one)
Environment vars    # Production (set in CI/CD)
```

---

## 5. Graceful Failure

### Fail Fast vs. Degrade Gracefully

```python
# Fail fast (development): raise immediately
if not api_key:
    raise ValueError("GROQ_API_KEY not set. Copy .env.example to .env")

# Degrade gracefully (production): try fallback
def get_llm_safe(providers=["groq", "openrouter", "gemini"]):
    for provider in providers:
        try:
            config = get_llm_config(provider)
            return config
        except ValueError:
            continue
    raise RuntimeError("No working LLM provider configured")
```

---

## 6. Testing Multi-Agent Systems

### Unit Test Individual Agents (No API Calls)

```python
def test_agent_system_message():
    agent = AssistantAgent(
        name="TestAgent",
        system_message="Always reply with: TEST_DONE",
        llm_config={"config_list": [{"model": "mock", "api_key": "x"}]}
    )
    assert "TEST_DONE" in agent.system_message
```

### Integration Test with Mock Responses

```python
from unittest.mock import patch

def test_research_pipeline():
    with patch("autogen.AssistantAgent.generate_oai_reply") as mock_llm:
        mock_llm.return_value = (True, "RESEARCH_DONE")
        # Test pipeline logic without API calls
        result = run_research_pipeline("test topic")
        assert result is not None
```

---

## Interview Questions

**Q: How do you handle rate limits in a production AutoGen system?**
A: Implement exponential backoff with jitter, use a multi-provider fallback config_list, and track per-provider usage to preemptively switch before hitting limits.

**Q: How do you monitor costs in production?**
A: Extract token usage from ChatResult objects, track per-run and cumulative costs in a database or time-series store, and set up alerts when costs exceed thresholds.

**Q: How do you test multi-agent conversations without making real API calls?**
A: Mock `generate_oai_reply()` to return predetermined responses, test the orchestration logic separately from the LLM quality, and use fixture files for expected outputs.
