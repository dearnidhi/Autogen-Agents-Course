
import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
# Load API key
from dotenv import load_dotenv
load_dotenv()
# =========================
# LLM CONFIG (GROQ)
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

# =========================
# GROUPCHAT BASIC EXAMPLE
# =========================

def run_feature_review(feature_request: str):

    print("\n==============================")
    print(" GROUPCHAT FEATURE REVIEW ")
    print("==============================\n")

    # LLM config load
    llm_config = get_config()


    # =========================
    # 1. PRODUCT MANAGER AGENT
    # =========================
    product_manager = AssistantAgent(
    name="ProductManager",
    system_message=(
            "You are a Product Manager. "
            "Check business value, user need, and priority. "
            "End with PM_DONE."
        ),

    llm_config=get_config()
)

    # =========================
    # 2. DEVELOPER AGENT
    # =========================
    developer = AssistantAgent(
    name="Developer",
    system_message=(
            "You are a Software Developer. "
            "Check feasibility, complexity, and risks. "
            "End with DEV_DONE."
        ),

    llm_config=get_config()
)

    # =========================
    # 3. UX DESIGNER AGENT
    # =========================
   
    ux_designer = AssistantAgent(
    name="UXDesigner",
    system_message=(
            "You are a UX Designer. "
            "Check user experience and usability. "
            "End with UX_DONE."
        ),

    llm_config=get_config()
)

    # =========================
    # 4. QA ENGINEER AGENT
    # =========================
    
    qa_engineer = AssistantAgent(
    name="QAEngineer",
    system_message=(
            "You are a QA Engineer. "
            "Find bugs, edge cases, and test scenarios. "
            "End with QA_DONE."
        ),

    llm_config=get_config()
)
    # =========================
    # USER CONTROLLER (ADMIN)
    # =========================
    admin = UserProxyAgent(
    name="Admin",
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=lambda msg: "QA_DONE" in (msg.get("content") or ""),
)

   
    # =========================
    # GROUP CHAT SETUP
    # =========================
    groupchat = GroupChat(
        agents=[product_manager,developer, ux_designer, qa_engineer ],
        messages= [],
        max_round=6,
        speaker_selection_method="auto"

    )

    manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config,
    is_termination_msg=lambda msg: "QA_DONE" in (msg.get("content") or ""),
)
   

    # =========================
    # START CHAT
    # =========================
   
    admin.initiate_chat(
        manager,
        message=f"Review this feature:\n\n{feature_request}"
            )

# =========================
# MAIN RUN
# =========================


if __name__ == "__main__":
    feature = """
    Smart Auto-Save System:
    Save document every 60 seconds and detect conflicts
    when multiple users edit at the same time.
    """
    run_feature_review(feature)
