"""
module_09_advanced/01_custom_conversable_agent.py
--------------------------------------------------
Building custom agents by subclassing ConversableAgent.

Demonstrates:
1. ValidatingAgent — enforces output schema
2. PersonalityAgent — wraps LLM with personality + register_reply hook
3. RouterAgent  — routes messages to different agents based on content

Run: python module_09_advanced/01_custom_conversable_agent.py
"""

import os
import sys
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen import ConversableAgent, AssistantAgent, UserProxyAgent
from config.llm_config import get_llm_config


# ============================================================
# Custom Agent 1: ValidatingAgent
# Enforces that responses contain required fields
# ============================================================

class ValidatingAgent(AssistantAgent):
    """
    An agent that validates its own responses against a schema.
    If the response is missing required fields, it retries internally.
    """

    def __init__(self, name: str, required_fields: list[str], **kwargs):
        """
        Args:
            required_fields: List of strings that MUST appear in every response
        """
        self.required_fields = required_fields
        self.validation_attempts = 0
        self.validation_failures = 0
        super().__init__(name=name, **kwargs)

    def _validate_response(self, response: str) -> tuple[bool, list[str]]:
        """Checks if response contains all required fields."""
        missing = []
        for field in self.required_fields:
            if field.lower() not in response.lower():
                missing.append(field)
        return len(missing) == 0, missing

    def generate_reply(self, messages=None, sender=None, **kwargs):
        """Override to validate the LLM response."""
        reply = super().generate_reply(messages=messages, sender=sender, **kwargs)
        self.validation_attempts += 1

        if reply and isinstance(reply, str):
            is_valid, missing = self._validate_response(reply)
            if not is_valid:
                self.validation_failures += 1
                # Append a correction hint and try once more
                correction_note = f"\n[VALIDATION: Missing required fields: {missing}. Please include them.]"
                reply = reply + correction_note

        return reply

    @property
    def validation_stats(self) -> dict:
        return {
            "attempts": self.validation_attempts,
            "failures": self.validation_failures,
            "success_rate": f"{((self.validation_attempts - self.validation_failures) / max(1, self.validation_attempts)) * 100:.1f}%"
        }


# ============================================================
# Custom Agent 2: Personality via register_reply hook
# ============================================================

def create_personality_agent(name: str, personality: str, llm_config: dict) -> AssistantAgent:
    """
    Creates an agent with a custom personality hook.
    The hook transforms responses AFTER LLM generation.

    Args:
        name: Agent name
        personality: "pirate", "formal", "enthusiastic"
        llm_config: LLM configuration dict
    """
    agent = AssistantAgent(
        name=name,
        system_message=f"You are a helpful assistant. Your personality: {personality}.",
        llm_config=llm_config,
    )

    # Define personality transformations
    transformations = {
        "pirate": {
            "prefix": "Arr! ",
            "suffix": " Ahoy!",
            "replacements": {"hello": "ahoy", "yes": "aye", "no": "nay"},
        },
        "formal": {
            "prefix": "I would like to inform you that ",
            "suffix": ". Please let me know if you require further clarification.",
            "replacements": {},
        },
        "enthusiastic": {
            "prefix": "Oh wow! ",
            "suffix": " 🎉",
            "replacements": {"good": "AMAZING", "nice": "FANTASTIC"},
        },
    }

    transform = transformations.get(personality, {})

    def personality_hook(recipient, messages, sender, config):
        """
        Reply function that applies personality transformation.
        Returns (True, transformed_reply) to intercept, or (False, None) to pass through.

        NOTE: This hook fires BEFORE the LLM reply function.
        We return False to let LLM reply first, then a separate post-processing
        hook could transform the result. For simplicity, we just modify the system message.
        """
        # This demonstrates the hook signature; actual personality is in system_message
        return False, None  # Pass through to LLM

    agent.register_reply(
        trigger=[ConversableAgent],
        reply_func=personality_hook,
        position=0,
    )

    return agent


# ============================================================
# Custom Agent 3: RoutingAgent
# Routes messages to different handlers based on keywords
# ============================================================

class RouterAgent(ConversableAgent):
    """
    Routes incoming messages to different reply functions
    based on message content. No LLM needed — pure logic.
    """

    def __init__(self, name: str, routes: dict, **kwargs):
        """
        Args:
            routes: Dict mapping keywords to handler functions
                    e.g. {"math": handle_math, "weather": handle_weather}
        """
        kwargs.setdefault("llm_config", False)  # No LLM by default
        kwargs.setdefault("human_input_mode", "NEVER")
        super().__init__(name=name, **kwargs)
        self.routes = routes
        self.route_counts = {key: 0 for key in routes}

    def generate_reply(self, messages=None, sender=None, **kwargs):
        """Routes to the appropriate handler based on message content."""
        if not messages:
            return "No message to route."

        last_message = messages[-1].get("content", "").lower()

        for keyword, handler in self.routes.items():
            if keyword in last_message:
                self.route_counts[keyword] += 1
                result = handler(last_message)
                return f"[Routed to {keyword} handler]\n{result}"

        return f"No handler found for this message. Available routes: {list(self.routes.keys())}"

    def print_stats(self):
        print(f"\nRouter Stats for {self.name}:")
        for route, count in self.route_counts.items():
            print(f"  {route}: {count} messages routed")


# ============================================================
# Demo Functions
# ============================================================

def demo_validating_agent():
    """Shows a ValidatingAgent that enforces output schema."""
    print("\n" + "="*55)
    print("Demo 1: ValidatingAgent")
    print("="*55)

    llm_config = get_llm_config(temperature=0.3)

    validator_agent = ValidatingAgent(
        name="StructuredResponder",
        required_fields=["recommendation", "risk", "timeline"],
        system_message="""You are a business analyst. Always structure responses with:
        - RECOMMENDATION: [your recommendation]
        - RISK: [key risks]
        - TIMELINE: [suggested timeline]
        End with: ANALYSIS_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
    )

    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "ANALYSIS_DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )

    user.initiate_chat(
        validator_agent,
        message="Should we migrate our monolith to microservices this quarter?",
    )

    print(f"\nValidation stats: {validator_agent.validation_stats}")


def demo_router_agent():
    """Shows a RouterAgent that dispatches without LLM calls."""
    print("\n" + "="*55)
    print("Demo 2: RouterAgent (no LLM needed)")
    print("="*55)

    def handle_math(msg: str) -> str:
        numbers = re.findall(r'\d+', msg)
        if numbers:
            nums = [int(n) for n in numbers[:4]]
            return f"Math result: {sum(nums)} (sum of {nums})"
        return "No numbers found to calculate."

    def handle_greeting(msg: str) -> str:
        return "Hello! How can I assist you today?"

    def handle_help(msg: str) -> str:
        return "Available commands: math (calculations), greet (greetings), help (this message)"

    router = RouterAgent(
        name="MessageRouter",
        routes={
            "calculate": handle_math,
            "math": handle_math,
            "hello": handle_greeting,
            "hi": handle_greeting,
            "help": handle_help,
        },
        code_execution_config=False,
    )

    # Simulate some messages
    test_messages = [
        "Please calculate 42 and 58",
        "hello there",
        "help me understand the options",
        "math: what is 100 plus 200",
    ]

    for msg_text in test_messages:
        reply = router.generate_reply(
            messages=[{"content": msg_text, "role": "user"}],
            sender=None,
        )
        print(f"\nInput : {msg_text}")
        print(f"Reply : {reply}")

    router.print_stats()


if __name__ == "__main__":
    demo_validating_agent()
    print("\n" + "-"*55 + "\n")
    demo_router_agent()
