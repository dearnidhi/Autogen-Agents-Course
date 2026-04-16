"""
Context Carryover Pipeline
-------------------------
Goal:
Show how one agent's output is passed to the next agent
so each stage becomes smarter.

Flow:
Stage 1 → Stage 2 (uses Stage 1)
Stage 2 → Stage 3 (uses Stage 1 + 2)
"""

# ============================================================
# STEP 1: IMPORTS + ENV SETUP
# ============================================================
import os
import sys
from dotenv import load_dotenv

# Fix path so project imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load API keys from .env file
load_dotenv()

from autogen import AssistantAgent, UserProxyAgent


# ============================================================
# STEP 2: LLM CONFIG (Groq + OpenRouter)
# ============================================================
def get_working_config(temperature: float = 0.7) -> dict:
    """
    Creates LLM config using available API keys.

    - Checks if GROQ or OPENROUTER keys exist
    - Adds available providers
    - Returns config for agents
    """

    config_list = []

    # Get API keys from environment
    groq_key = os.getenv("GROQ_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    print("\nChecking API keys...")

    # Add Groq (fast)
    if groq_key:
        config_list.append({
            "model": "llama-3.1-8b-instant",
            "api_key": groq_key,
            "api_type": "groq",
        })
        print("✓ Groq added")

    # Add OpenRouter (backup)
    if openrouter_key:
        config_list.append({
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "api_key": openrouter_key,
            "base_url": "https://openrouter.ai/api/v1",
        })
        print("✓ OpenRouter added")

    # If no keys found → error
    if not config_list:
        raise ValueError("No API keys found. Check your .env file.")

    return {
        "config_list": config_list,
        "temperature": temperature,
    }


# ============================================================
# STEP 3: MAIN PIPELINE FUNCTION
# ============================================================
def run_staged_analysis(dataset_description: str) -> None:
    """
    Runs 3-stage pipeline with context carryover.

    Stage 1 → Basic analysis
    Stage 2 → Deep analysis (uses Stage 1)
    Stage 3 → Recommendations (uses Stage 1 + 2)
    """

    # Get LLM config
    llm_config = get_working_config(temperature=0.6)

    # Create ONE proxy to control all conversations
    analyst_proxy = UserProxyAgent(
        name="DataProxy",
        human_input_mode="NEVER",
        code_execution_config=False,

        # Stop when agent says DONE
        is_termination_msg=lambda msg: "DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
    )

    # ============================================================
    # STAGE 1: BASIC ANALYSIS
    # ============================================================
    print("\n===== STAGE 1: BASIC ANALYSIS =====")

    surface_analyst = AssistantAgent(
        name="SurfaceAnalyst",
        system_message="""
        Give 3-5 simple insights about the data.
        Keep it short.
        End with DONE
        """,
        llm_config=llm_config,
    )

    result1 = analyst_proxy.initiate_chat(
        surface_analyst,
        message=f"Analyze this data:\n{dataset_description}",
        clear_history=True,
    )

    # Extract ONLY final message
    stage1_summary = result1.chat_history[-1]["content"].strip()

    print("✓ Stage 1 complete")

    # ============================================================
    # STAGE 2: DEEP ANALYSIS (USES STAGE 1)
    # ============================================================
    print("\n===== STAGE 2: DEEP ANALYSIS =====")

    pattern_analyst = AssistantAgent(
        name="PatternAnalyst",
        system_message="""
        Find deeper patterns and reasons.
        Use previous analysis.
        End with DONE
        """,
        llm_config=llm_config,
    )

    result2 = analyst_proxy.initiate_chat(
        pattern_analyst,
        message="Find deeper insights",

        # 👇 MAIN CONCEPT: PASS STAGE 1 RESULT
        carryover=stage1_summary,

        clear_history=True,
    )

    stage2_summary = result2.chat_history[-1]["content"].strip()

    print("✓ Stage 2 complete")

    # ============================================================
    # STAGE 3: RECOMMENDATIONS (USES STAGE 1 + 2)
    # ============================================================
    print("\n===== STAGE 3: RECOMMENDATIONS =====")

    strategist = AssistantAgent(
        name="Strategist",
        system_message="""
        Give 3 actionable recommendations.
        Use all previous analysis.
        End with DONE
        """,
        llm_config=llm_config,
    )

    # Combine both previous outputs
    combined_context = stage1_summary + "\n" + stage2_summary

    result3 = analyst_proxy.initiate_chat(
        strategist,
        message="Give final recommendations",

        # 👇 PASS BOTH STAGE RESULTS
        carryover=combined_context,

        clear_history=True,
    )
    # ============================================================
    # FINAL OUTPUT (SHORT)
    # ============================================================
    print("\n===== FINAL OUTPUT =====")
    # Print only first 300 characters (clean terminal)
    print(result3.summary[:300])
# ============================================================
# STEP 4: RUN PROGRAM
# ============================================================
if __name__ == "__main__":
    # Sample dataset
    sample_data = """
    E-commerce metrics:
    Jan: 1200 orders, $45k revenue
    Feb: 1450 orders, $52k revenue
    Mar: 1100 orders, $38k revenue

    Categories:
    Electronics (high value), Clothing (mid), Books (low)

    Customers:
    30% new, 70% returning
    """
    # Run pipeline
    run_staged_analysis(sample_data)