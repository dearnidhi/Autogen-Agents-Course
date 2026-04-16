import os
import math
from autogen import AssistantAgent, UserProxyAgent, register_function
from dotenv import load_dotenv
load_dotenv()


# =========================
# LLM CONFIG (Groq)
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
        "temperature": 0.5,
    }


# =============================
# TOOLS (Function the AI can use)
# =============================  
def get_python_tip(topic: str) -> str:
    """
    Tool 1:
    Returns a Python tip based on topic.
    The Assistant will call this instead of generating from memory.
    """
    tips = {
        "decorators": "Use functools.wraps() inside decorators.",
        "lists": "Use list comprehensions for cleaner code.",
    }

    # Convert topic to lowercase and return matching tip
    return tips.get(topic.lower(), "No tip found.")



def calculate(expression: str) -> str:
    """
    Tool 2:
    Safely evaluates a math expression.
    Example: 'sqrt(144) + pi'
    """
    try:
        # eval() is restricted for safety (no builtins allowed)
        result = eval(expression, {
            "__builtins__": {},
            "sqrt": math.sqrt,
            "pi": math.pi
        })
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"


# =========================
# MAIN DEMO (Agent + Tool Flow)
# =========================
def main():

    # AssistantAgent = "Brain"
    # Decides WHEN to use tools and WHAT to ask
    assistant = AssistantAgent(
        name="Assistant",
        system_message="""
        You are a helpful assistant.
        Use tools when needed.
        After answering, say DONE""",
        llm_config=get_config(),
    )

    # UserProxyAgent = "Executor"
    # Actually RUNS the tools (functions)
    proxy = UserProxyAgent(
        name="Executor",
        human_input_mode="NEVER",  # No manual input needed
        code_execution_config=False,  # No Python code execution, only tools
        is_termination_msg=lambda msg: "DONE" in (msg.get("content") or ""),
    )

    # =========================
    # Register tools
    # =========================
    # This connects Python functions to the AI

    register_function(
        get_python_tip,
        caller=assistant,   # Assistant decides when to use it
        executor=proxy,     # Proxy executes the function
        name="get_python_tip",
        description="Get Python tips",
    )    

    register_function(
        calculate,
        caller=assistant,
        executor=proxy,
        name="calculate",
        description="Solve math expressions",
    )

     # =========================
    # Start conversation
    # =========================
    # This is the user input given to the AI

    proxy.initiate_chat(
        assistant,
        message="""
        1. Give me a Python tip about decorators
        2. What is sqrt(144) + pi?
        Use tools.
        """,
    )
# Entry point of program
if __name__ == "__main__":
    main()    