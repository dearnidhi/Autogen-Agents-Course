"""
module_03_conversation_patterns/01_two_agent_basic.py
------------------------------------------------------
Core two-agent conversation patterns with result capture.

Concepts:
- Capturing chat results (summary, cost, chat_history)
- Using max_turns instead of is_termination_msg
- The Creator-Critic improvement loop
- chat_messages inspection for debugging

Run: python module_03_conversation_patterns/01_two_agent_basic.py
"""

# -----------------------------------------
# Basic Python imports
# -----------------------------------------
import os   # Used to read environment variables (API keys)
import sys  # Used to modify Python path
from dotenv import load_dotenv  # Loads .env file
# Load .env file (VERY IMPORTANT)
load_dotenv()

# Add project root so we can import config/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -----------------------------------------
# AutoGen imports
# -----------------------------------------
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
# AssistantAgent → AI brain
# UserProxyAgent → sends tasks automatically
from config.llm_config import get_llm_config


# -----------------------------------------
# DEMO 1: CAPTURING CONVERSATION RESULT
# -----------------------------------------

def demo_result_capture()->None:
    """ 
    what data we get after a converstation end.
    we get: summery , cost cost info, full chat history
    """

    print("\n" + "=" * 55)
    print("🚀 Demo 1: capturing chat result ")
    print("=" * 55)

    # step 1 configure llm
    llm_config = get_llm_config(temperature=0.5)
    
    # step 2: Create Assistant 
    # assistant (AI)
    assistant = AssistantAgent(
        name="DataExpert",
        system_message="Explain Python data types concisely. End with: EXPLAIN_DONE",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,)
    
    # Create User Proxy
    user = UserProxyAgent(
        name="Learner",
        human_input_mode="NEVER",  # Fully automatic
        code_execution_config=False,
        max_consecutive_auto_reply=1,
        is_termination_msg=lambda msg: "EXPLAIN_DONE" in msg.get("content", ""),
    )
    
    # Start conversation
    result = user.initiate_chat(
        assistant,
        message="Explain Python's 5 main built-in data types briefly.",  # What to ask
        summary_method="last_msg"
    )

    # STEP 5: DISPLAY THE RESULTS ON SCREEN
    # This shows what we captured from the conversation
    print("\n--- Chat Result ---")
    print(f"Messages exchanged: {len(result.chat_history)}")
    # Show how many messages were sent back and forth
    print(f"Summary: {result.summary[:100] if result.summary else 'None'}...")
    # Show first 100 characters of the summary


# ============================================================
# DEMO 2: CREATOR-CRITIC PATTERN
# ============================================================
def demo_creator_critic() -> None:
    """
    This demo shows the improvement loop pattern:
    - Writer creates content
    - Critic reviews and asks for changes
    - Writer revises until critic approves
    
    This  produce BETTER quality than a single agent can do alone"""
    print("\n" + "="*55)
    print("Demo 2: Creator-Critic Pattern")
    print("="*55)
    # step 1 configure llm
    llm_config = get_llm_config(temperature=0.7)

    # STEP 2: Create the WRITER AGENT (The Creator)
    # This agent creates the initial content
 
    
    writer = AssistantAgent(
        name="PythonWriter",
        system_message="""You write clear Python tutorials.
                When asked to create, produce clean content.
                When criticized, revise specifically what was pointed out.
                Accept criticism graciously.
                When the critic says APPROVED, say WRITING_COMPLETE.""",
                # These instructions tell the writer:
                # - Write clearly
                # - When criticized, fix exactly what was mentioned
                # - Be polite about criticism
                # - When critic says APPROVED, say WRITING_COMPLETE to end
        llm_config=llm_config,
        max_consecutive_auto_reply=4,)
    

    # STEP 3: Create the CRITIC AGENT (The Reviewer)
    # This agent reviews and requests improvements

    critic = AssistantAgent(
        name="QualityCritic",

        system_message="""You are a harsh but fair Python tutorial reviewer.
        Review for:
        1. Clarity (would a beginner understand it?)
        2. Accuracy (is the code correct?)
        3. Completeness (are key points covered?)

        Give ONE specific improvement request per review round.
        If the tutorial meets all criteria, say APPROVED.
        Limit to 2 rounds of critique maximum.""",
        # These instructions tell the critic:
        # - Check clarity, accuracy, completeness
        # - Give ONE specific thing to fix each time
        # - Say APPROVED when it's good
        # - Maximum 2 rounds of feedback

        llm_config=llm_config,
        max_consecutive_auto_reply=4,
    )
    # This agent reviews and request improvements
   


    # STEP 4: START THE CONVERSATION
    # The critic starts the conversation by asking the writer to create something

    result = critic.initiate_chat(
            writer,  # Critic talks to writer
            message="""Write a 3-sentence explanation of Python list comprehensions.
            Include one simple example.
            I will review and you must revise if needed.""",
            # The critic gives the task
            is_termination_msg=lambda msg: "WRITING_COMPLETE" in msg.get("content", ""),
            # Stop when writer says WRITING_COMPLETE
        )

    print(f"\n--- Result: {len(result.chat_history)} total messages ---")


# ============================================================
# DEMO 3: USING max_turns
# ============================================================
def demo_max_turns() -> None:
    """
    This demo shows a simpler way to control conversation length.
    max_turns stops after exactly N exchanges.
    
    This is easier than using is_termination_msg.
    """
    print("\n" + "="*55)
    print("Demo 3: max_turns Control")
    print("="*55)
    # step 1 configure llm
    llm_config = get_llm_config(temperature=0.8)#more creative for brainstorming

    # STEP 2: Create BRAINSTORMER AGENT
    # This agent generates creative ideas
    brainstormer = AssistantAgent(
        name="IdeaBot",
        system_message="Generate creative Python project ideas. One idea per message.",
        llm_config=llm_config,
        max_consecutive_auto_reply=5,
    )
    # STEP 3: Create COLLECTOR AGENT
    # This agent collects the ideas
    collector = UserProxyAgent(
        name="IdeaCollector",
        human_input_mode="NEVER",
        code_execution_config=False,
        max_consecutive_auto_reply=5,
    )
    # STEP 4: START THE CONVERSATION
    # max_turn =2 means exactly  2 exchanges (collector asks, brainstoremer answer, done)
    try:
        result = collector.initiate_chat(
            brainstormer,
            message="Give me a Python project idea for a beginner portfolio.",
            max_turns=2, #Only 2 exchanges
        )
        print(f"\nCollected {len(result.chat_history)} messages in 2 turns")

    except TypeError:
        # If AutoGen  version is old and doesn't support max_turns
        print("max_turns not supported in this version — using max_consecutive_auto_reply instead")
        collector.max_consecutive_auto_reply = 2

        result = collector.initiate_chat(
            brainstormer,
            message="Give me a Python project idea for a beginner portfolio.",
        )
# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    # Run the demos one by one
    demo_result_capture()      # Demo 1: Capture results
    demo_creator_critic()      # Demo 2: Creator-Critic pattern
    demo_max_turns()         # Demo 3: max_turns (commented to save tokens)

    