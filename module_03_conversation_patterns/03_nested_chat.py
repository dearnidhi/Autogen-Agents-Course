"""
module_03_conversation_patterns/03_nested_chat.py
--------------------------------------------------
NESTED CHATS - One agent talks to another agent BEFORE answering

SIMPLE EXPLANATION :
----------------------------------
Imagine you're a manager. A client asks you a technical question.
Instead of guessing, you say: "Let me ask my expert first!"

You go to the expert, get their opinion, then come back with a better answer.

That's nested chat! One agent (manager) asks another agent (expert) for help
before responding to the user.

EXAMPLE:
--------
User: "Should we rebuild our app?"
Manager: "Let me check with my tech expert..."
Manager asks TechExpert
TechExpert says: "Yes, but it will take 3 months"
Manager: "Based on my expert, yes, but expect 3 months of work"

See? Better answer because manager consulted an expert!
"""

# ============================================================
# STEP 1: IMPORT NECESSARY LIBRARIES
# ============================================================

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
from autogen import AssistantAgent, UserProxyAgent
# AssistantAgent → AI brain
# UserProxyAgent → helper that manage conversation

from config.llm_config import get_llm_config
from typing import Optional 


# ============================================================
# DEMO 1: SIMPLE NESTED CHAT
# ============================================================

def demo_simple_nested()->None:
    """
    HOW IT WORKS:
    1. Inner chat: Research agent provides facts
    2. Outer chat: Writer agent uses those facts to write
    """
    print("\n" + "="*55)
    print("Simple Nested Chat (manual version)")
    print("="*55)


    # ============================================================
    # STEP 1: SETUP - Configure the AI
    # ============================================================
    # Get LLM configuration (temperature controls creativity)    
    llm_config = get_llm_config(temperature=0.6)

    
    # ============================================================
    # PART 1: INNER CHAT (RESEARCH PHACE)
    # ============================================================
    # This agent specializes in providing facts

    researcher = AssistantAgent(
        name="Researcher",
        system_message="""Research Python topics. Provide 3 key facts. End: RESEARCH_DONE""", 
        llm_config=llm_config,
        max_consecutive_auto_reply=1,
        )

    # Create ONE coordinator that will manage ALL conversation
    inner_proxy = UserProxyAgent(
        name="InnerProxy",
        human_input_mode="NEVER",  # Fully automatic
        code_execution_config=False,
        is_termination_msg=lambda msg: "RESEARCH_DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
        )

     # START THE RESEARCH CONVERSATION
    research = inner_proxy.initiate_chat(
            researcher,
            message="Key facts about Python async/await",
            summary_method="last_msg",
        )    
    # ============================================================
    # PART 2: OUTER CHAT (WRITING PHACE)
    # ============================================================    
    
     
    # Create a WRITER agent (EXPERT WHO WRITE NICELY)  
    writer = AssistantAgent(
        name="Writer",
        system_message="Write beginner-friendly explanations. End: WRITING_DONE",
        max_consecutive_auto_reply=1,
        llm_config=llm_config,
        )  


    # Create ONE PROXY FOR WRITING CONVERSATION 
    outer_proxy = UserProxyAgent(
        name="OuterProxy",
        human_input_mode="NEVER",  # Fully automatic
        code_execution_config=False,
        is_termination_msg=lambda msg: "WRITING_DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
        )

  # START THE writing CONVERSATION
    final = outer_proxy.initiate_chat(
            writer,  
            message=f"Write a 3-sentence beginner explanation using: {research.summary}",     
        ) 
    #show the final result
    print(f"\n complete. final output:\n{final.summary[:300]}")  

# ============================================================
# DEMO 2: ADVANCED NESTED CHAT (AUTOMATIC CONSULTATION)
# ============================================================
def demo_consultation_pattern() -> None:
    """ HOW IT WORKS:
        - ProjectManager automatically consults TechExpert before replying
        - No manual steps - all automatic!
        - Uses custom reply functions """


    print("\n" + "="*55)
    print("Nested Chat: Manager Consults Expert")
    print("="*55)

    # Get LLM configuration (temperature controls creativity)    
    llm_config = get_llm_config(temperature=0.7)

        
    # ============================================================
    # STEP 1: CREATE THE EXPERT  (WHO WILL BE CONSULTED)
    # ============================================================
    
    tech_expert = AssistantAgent(
        name="TechExpert",
        system_message="""You are a senior software architect.
        Give technical assessments: feasibility, risks, estimated complexity.
        Be direct. End with: TECH_ASSESSMENT_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,

    )

    # Create ONE PROXY FOR WRITING CONVERSATION 
    inner_proxy = UserProxyAgent(
        name="ConsultationProxy",
        human_input_mode="NEVER",  # Fully automatic
        code_execution_config=False,
        is_termination_msg=lambda msg: "TECH_ASSESSMENT_DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
        )

    
# ============================================================
# STEP 2: CONSULTATION FUNCTION
# ============================================================
    def consult_expert(topic: str)->str:  
        """
        Input: Topic/question to ask the expert
        Output: Expert's assessment
        """  
        print(f"\n  [Manager consulting TechExpert about: {topic[:50]}...]")
        result = inner_proxy.initiate_chat(
            tech_expert,
            message=f"Quick assessment:{topic}", 
            summary_method="last_msg",  # Just take the last message (simpler)
            clear_history=True,  # Fresh conversation 
        )
        return result.summary  

    # ============================================================
    # STEP 3: CUSTOM REPLY FUNCTION (THE MAGIC!)
    # ============================================================
    def manager_reply(recipient: AssistantAgent, messages: list, sender: "UserProxyAgent", config: Optional[dict],):
        #step 1: get what makes it nasted
        last_message = messages[-1].get("content","") if messages else ""  
        # step 2: Ask the expert (nested chat)
        expert_view = consult_expert(last_message)  

        # step 3: combine user Q and expert ans
        synthesis_prompt = f"""
        The user asked: {last_message}

        My tech expert says: {expert_view}

        Based on this assessment, provide a brief project recommendation
        in 3-4 sentences, then say MANAGER_DONE.
        """

        # ============================================================
        # STEP 4: use a synthesizer to create final answer
        # ============================================================
        manager = AssistantAgent(
            name="ManagerSynthesizer",
            system_message="Synthesize technical input into project decisions.",
            llm_config=get_llm_config(temperature=0.6),
            max_consecutive_auto_reply=1,

        )
        inner_proxy2 = UserProxyAgent(
            name="SynthProxy",
            human_input_mode="NEVER",  # Fully automatic
            code_execution_config=False,
            is_termination_msg=lambda msg: "MANAGER_DONE" in msg.get("content", ""),
            max_consecutive_auto_reply=0,
            )
        #step 5 final ans
        result = inner_proxy2.initiate_chat(
            manager,
            message=synthesis_prompt,  
            clear_history=True,  # Fresh conversation 
        )
        return True, result.summary   

    # ============================================================
    # STEP 5: CREATE THE MANAGER AGENT
    # ============================================================

    project_manager = AssistantAgent(
        name="ProjectManager",
        system_message="You are a project manager who consults experts.",
        llm_config=llm_config,
        max_consecutive_auto_reply=1
    )

    # REGISTER the custom reply func
    # this tells the manager : "hey use this special func when replying"
    # think of it as : "before you answer , always ask the expert first"
    project_manager.register_reply(
        trigger = UserProxyAgent,
        reply_func = manager_reply,
        position = 0,

    )

    # ============================================================
    # STEP 5: START THE CONVERSATION
    # ============================================================

    user = UserProxyAgent(
        name="Stackholder",  
        human_input_mode="NEVER",  # Fully automatic
        code_execution_config=False,
        is_termination_msg=lambda msg: "MANAGER_DONE" in msg.get("content", ""),
        max_consecutive_auto_reply=1,
        )
    
    # This single line triggers the entire nested chat!
    user.initiate_chat(
        project_manager,
        message="Should we rebuild our monolithic Python app as microservices? We have a team of 5 developers.",
    )    
# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    # Run the simple version (easier to understand)
    #demo_simple_nested()
    
    # Uncomment below to try the advanced version
    demo_consultation_pattern()  # More complex, uses more token
