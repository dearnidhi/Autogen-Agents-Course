# Lesson 01: Building Custom Agents

## Why Custom Agents?

The built-in `AssistantAgent` and `UserProxyAgent` cover 80% of use cases.
But sometimes you need an agent that:
- Has persistent state across conversations
- Enforces specific input/output schemas
- Has domain-specific validation logic
- Wraps an external service transparently

---

## The ConversableAgent Base Class

All AutoGen agents inherit from `ConversableAgent`. You can subclass it directly:

```python
from autogen import ConversableAgent

class MyCustomAgent(ConversableAgent):
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.my_state = {}  # Custom state

    def generate_reply(self, messages, sender, **kwargs):
        # Custom logic here
        last_message = messages[-1]["content"]
        # Process, transform, route...
        return "My custom reply"
```

---

## Two Ways to Customize

### 1. Register Custom Reply Functions (Recommended)
Add hooks to existing agents without subclassing:

```python
def my_reply_function(recipient, messages, sender, config):
    last = messages[-1]["content"]
    if "urgent" in last.lower():
        return True, "⚡ URGENT FLAGGED — escalating immediately"
    return False, None  # Fall through to default behavior

agent.register_reply(
    trigger=[ConversableAgent],  # When to activate
    reply_func=my_reply_function,
    position=0,  # 0 = highest priority
)
```

### 2. Subclass ConversableAgent
Best for agents needing persistent state or completely custom behavior:

```python
class StatefulAgent(ConversableAgent):
    DEFAULT_CONFIG = {"temperature": 0.5}

    def __init__(self, name, custom_param=None, **kwargs):
        system_msg = kwargs.pop("system_message", "You are helpful.")
        super().__init__(name=name, system_message=system_msg, **kwargs)
        self.custom_param = custom_param
        self.interaction_count = 0
        self.memory = []
```

---

## Agent State Patterns

### In-memory state (single session)
```python
class TrackingAgent(ConversableAgent):
    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.topics_discussed = set()
        self.response_times = []
```

### Persistent state (cross-session)
```python
import json
from pathlib import Path

class PersistentAgent(ConversableAgent):
    def __init__(self, name, state_file="agent_state.json", **kwargs):
        super().__init__(name=name, **kwargs)
        self.state_file = Path(state_file)
        self.state = self._load_state()

    def _load_state(self):
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {"interactions": 0, "memory": []}

    def _save_state(self):
        self.state_file.write_text(json.dumps(self.state, indent=2))
```

---

## When to Use What

| Scenario | Approach |
|----------|----------|
| Need specific system message behavior | AssistantAgent with custom system_message |
| Need to pre/post-process messages | register_reply() hook |
| Need persistent state | Subclass ConversableAgent |
| Need external service integration | Subclass + tool registration |
| Need schema validation | Subclass with validation in generate_reply |

---

## Interview Questions

**Q: What's the difference between `register_reply()` and subclassing?**
A: `register_reply()` adds a function to the reply chain without modifying the agent class — good for targeted hooks. Subclassing gives full control over agent behavior and state — better for fundamentally different agents.

**Q: How does AutoGen decide which reply function to call?**
A: AutoGen iterates `self._reply_func_list` in order. Each function returns `(True, reply)` if it handles the message, or `(False, None)` to pass to the next. The first match wins.

**Q: Can a custom agent still use LLM calls?**
A: Yes. Call `self.generate_oai_reply(messages, sender)` from within your custom `generate_reply()` to use the underlying LLM, then post-process the result.
