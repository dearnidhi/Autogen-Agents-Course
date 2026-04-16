"""module_03_conversation_patterns/02_sequential_pipeline.py
----------------------------------------------------------
SEQUENTIAL PIPELINE - Chain multiple conversations together

WHAT IS THIS?
------------
Think of it like an assembly line in a factory:
- Stage 1: Research (gather raw materials)
- Stage 2: Outline (arrange materials into structure)
- Stage 3: Write (create final product)

Each stage is a SEPARATE conversation between two agents.
The OUTPUT of one stage becomes the INPUT for the next stage.

WHY IS THIS USEFUL?
------------------
- Each agent specializes in one task (better quality)
- You can easily swap out stages
- You can debug each stage independently
- Real-world content creation follows this pattern

REAL-WORLD ANALOGY:
------------------
Building a house:
1. Architect (Research) → Understand requirements
2. Designer (Outline) → Create blueprints  
3. Builder (Write) → Construct the house

Run this file: python module_03_conversation_patterns/02_sequential_pipeline.py
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
# UserProxyAgent → coordinator that manage conversation

from config.llm_config import get_llm_config

# ============================================================
# STEP 2: MAIN PIPELINE FUNCTION
# ============================================================

def run_content_pipeline(topic: str)->dict:
    """
    
    INPUT:  topic (string) - What you want to write about
            Example: "Python list comprehensions for beginners"
    
    OUTPUT: dictionary (dict) - Contains results from all stages
            {
                "research": "Research results text...",
                "outline": "Article outline text...",
                "draft": "Article draft text..."
            }
    
      Returns results from each stage.

    """

    # ============================================================
    # STEP 2.1: SETUP - Configure the AI
    # ============================================================
    # Get LLM configuration (temperature controls creativity)    

    llm_config = get_llm_config(temperature=0.5)

    # Create ONE coordinator that will manage ALL conversation
    coordinator = UserProxyAgent(
        name="Coordinator",
        human_input_mode="NEVER",  # Fully automatic
        code_execution_config=False,
        is_termination_msg=lambda msg: any(
            tag in msg.get("content", "")
            for tag in ["STAGE_DONE", "DONE"]
        ),
        max_consecutive_auto_reply=1,
    )
    #store all result
    results = {}

    # ============================================================
    # STAGE 1: RESEARCH STAGE
    # ============================================================
    # Purpose: Gather facts and key information about the topic   

    print("\n" + "="*55)
    print("STAGE 1: RESEARCH - STAGE")
    print("="*55)

    researcher = AssistantAgent(
        name="Researcher",
        system_message="""You are a research expert.
        For any topic, provide:
        1. 3-5 key facts
        2. 2 intresting angles/prespectives
        3. Target audience: begginer | intermediate | expert
        Be factual and concise. END with: STAGE_DONE
        """,
        llm_config=llm_config,
        max_consecutive_auto_reply=2,
        )
    
    # START THE RESEARCH CONVERSATION
    research_result = coordinator.initiate_chat(
            researcher,
            message=f"Research this topic for an article: {topic}", # What to ask
            summary_method="reflection_with_llm",
            #reflection_with_llm use ai to create a good summery
            clear_history=True # start with fresh conversation
        )

    
    # Save the research results in our dictionary
    results["research"] = research_result.summary
    print(f"\n✓ Research complete. Summary length: {len(results['research'])} characters")
    print(" (That's about {:.0f} sentences)".format(len(results['research']) / 50)) 

    # ============================================================
    # STAGE 2: OUTLINE STAGE
    # ============================================================
    # Purpose: Create a structured outline from the research

    print("\n" + "="*55)
    print("STAGE 2: Outline - Creating Structure")
    print("="*55)   

    #Create an OUTLINER agent

    outliner = AssistantAgent(
        name="Outliner",
        system_message="""You create detailed article outlines.
        Structure:
        - Title (engaging, SEO-friendly)
        - Introduction hook
        - 3-4 main sections with sub-points
        - Conclusion approach
        End with: STAGE_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=1,
    )

     # START THE OUTLINE CONVERSATION
     # IMPORTANT :  We pass the research result to outliner
     # this is how information flows stage to stage
    outline_result = coordinator.initiate_chat(
            outliner,
            message=f"""Create an article outline using this research:
            {results['research']}
            Topic: begginer developers""",
            summary_method="reflection_with_llm",
            #reflection_with_llm use ai to create a good summery
            clear_history=True # start with fresh conversation

        )
    # save the outline result
    results["outline"] = outline_result.summary
    print(f"\n Outline complete. summary length:{len(results['outline'])} characters")

     
    # ============================================================
    # STAGE 3: DRAFT STAGE
    # ============================================================
    # Purpose: Write the actual article from the outline
    
    print("\n" + "="*55)
    print("STAGE 3: Draft - Writing Content")
    print("="*55)
    
    # Create a WRITER agent (specialized AI for writing)  
    writer = AssistantAgent(
        name="Writer",
        system_message="""You write engaging technical articles.
        Based on an outline, write the title + introduction only.
        The introduction should:
        - Hook the reader in sentence 1
        - State what they'll learn
        - Be 2-3 paragraphs max
        End with: STAGE_DONE""",
        llm_config=llm_config,
        max_consecutive_auto_reply=2,

        )  
    # START THE WRITING CONVERSATION
    # We pass the OUTLINE results to the writer

    draft_result= coordinator.initiate_chat(
        writer,
        message=f"""Write the title and introduction using this outline:
       {results['outline']}""" ,
        summary_method="last_msg",  # Just take the last message (simpler)
        clear_history=True,  # Fresh conversation with writer
    )

    # Save the draft results
    results["draft"] = draft_result.summary
    print(f"\n✓ Draft 6.")
    
    # Return all results so other functions can use them
    return results

# ============================================================
# STEP 3: DISPLAY RESULTS FUNCTION
# ============================================================
def print_pipeline_results(results: dict, topic: str) -> None:
    """
    This function prints ALL the results in a nice, organized way.
    
    INPUT: 
        results (dictionary) - Contains all stages' outputs
        topic (string) - The original topic we started with
    
    OUTPUT: Nothing (just prints to screen)
    """
    print("\n" + "="*55)
    print(f"PIPELINE COMPLETE: {topic}")
    print("="*55)

    print(f"\n📋 Stages completed: {len(results)}")

    # FIX 3: Added loop to print actual content from each stage
    for stage, output in results.items():
        print(f"\n--- {stage.upper()} ---")
        # Print first 500 characters of each stage
        if len(output) > 500:
            print(output[:500] + "...")
        else:
            print(output)


    print("\n" + "="*55)
    print("✅ Pipeline execution complete!")
    print("   You now have: Research → Outline → Draft")
    print("="*55)

# ============================================================
# STEP 4: MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    """
    This is the MAIN entry point - runs when you execute this file.
    
    WHAT HAPPENS HERE:
    1. Define what topic to write about
    2. Run the entire pipeline
    3. Display the beautiful results
    """
    
    # Define the topic we want to write about
    # You can change this to any topic you want!
    topic = "Python list comprehensions for beginners"
    print(f"🚀 Starting content pipeline for: {topic}")
    print("This will run 3 stages: Research → Outline → Draft\n")
    
    # RUN THE PIPELINE - This is where all the magic happens!
    results = run_content_pipeline(topic)
    
    # DISPLAY THE RESULTS - See what we created!
    print_pipeline_results(results, topic)


