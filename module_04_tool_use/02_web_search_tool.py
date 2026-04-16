import os
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent, register_function

load_dotenv()

# Simple LLM config (Groq only)
llm_config = {
    "config_list": [{
        "model": "llama-3.1-8b-instant",
        "api_key": os.getenv("GROQ_API_KEY"),
        "api_type": "groq",
    }],
    "temperature": 0.6,
}

# Fake search tool (simple)
def web_search(query: str, num_results: int = 3) -> str:
    return f"Results for '{query}' (simulated)."

# Create agents
researcher = AssistantAgent(
    name="Researcher",
    system_message="Search using tool and answer. End with RESEARCH_COMPLETE",
    llm_config=llm_config,
)

proxy = UserProxyAgent(
    name="Proxy",
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=lambda msg: "RESEARCH_COMPLETE" in msg.get("content", ""),
)

# Register tool
register_function(
    web_search,
    caller=researcher,
    executor=proxy,
    name="web_search",
    description="Search the web"
)

# Run
if __name__ == "__main__":
    proxy.initiate_chat(
        researcher,
        message="Search about Python programming"
    )