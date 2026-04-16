
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from dotenv import load_dotenv
import os

load_dotenv()


# =========================
# LLM CONFIG
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
        "temperature": 0.7,
    }

def run_conditional_pipeline(task: str):

    print("\n===== CUSTOM SPEAKER SELECTION PIPELINE =====\n")

    llm_config = get_config()

    # =========================
    # AGENTS
    # =========================
    researcher = AssistantAgent(
        name="Researcher",
        system_message="""Give ONLY 3 short points.
        Max 2 lines each.

        If technical → write TECHNICAL_CONTENT
        Else → GENERAL_CONTENT

        End with: RESEARCH_DONE""",
        llm_config=llm_config
    )

    tech_writer = AssistantAgent(
        name="TechWriter",
        system_message="""Write a SHORT technical explanation.
        Max 5 lines.
        No long paragraphs.

        End with: TECH_DONE""",
        llm_config=llm_config
    )

    content_writer = AssistantAgent(
        name="ContenthWriter",
        system_message="""Write simple explanation.
        Max 5 lines.
        Easy English only.

        End with: WRITE_DONE""",
        llm_config=llm_config
    )

    editor = AssistantAgent(
        name="Editor",
                
        system_message="""Improve and finalize content.
        Keep it SHORT (max 6 lines).

        End with: EDIT_DONE""",
        llm_config=llm_config
    )

    admin = UserProxyAgent(
        name="Admin",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "EDIT_DONE" in (msg.get("content") or ""),
    )

    # =========================
    # STATE TRACKER
    # =========================
    state = {
        "step":"research", # start with research
        "is_technical":False # flag to check if topic is technical
    }


    # =========================
    # SPEAKER CONTROLLER
    # =========================
    def selector(last_speaker, groupchat: GroupChat):

        messages = groupchat.messages   # get all chat messages
        last_msg = messages[-1].get("content", "") if messages else ""  
        # get last message content (used to decide next agent)

        # -------------------------
        # STEP 1: RESEARCH PHASE
        # -------------------------
        if state["step"] == "research":
            state["step"] = "write"   # move to next step (writing phase)

            # check if task contains technical keywords
            if "python" in task.lower() or "code" in task.lower():
                state["is_technical"] = True   # mark as technical topic
            else:
                state["is_technical"] = False  # mark as general topic

            return researcher   # first speaker will always be Researcher
        # -------------------------
        # STEP 2: WRITING PHASE
        # -------------------------
        elif state["step"] == "write":
            state["step"] = "edit"   # move to editing phase

            # if research output OR task indicates technical content
            if "TECHNICAL_CONTENT" in last_msg:
                print("→ Routing to TechWriter (technical content)")
                return tech_writer   # send to technical writer
            else:
                print("→ Routing to ContentWriter (general content)")
                return content_writer   # send to normal writer
       
        # -------------------------
        # STEP 3: EDITING PHASE
        # -------------------------
        elif state["step"] == "edit":
            state["step"] = "done"   # mark pipeline complete
            return editor            # final step → Editor

        # fallback (safety exit)
        return admin   # if something breaks, return control to Admin

    # =========================
    # GROUP CHAT
    # =========================
    groupchat = GroupChat(
        agents=[admin, researcher, tech_writer, content_writer, editor],
        messages= [],
        max_round=6,
        speaker_selection_method=selector

    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: "EDIT_DONE" in (msg.get("content") or ""),
    )

    # Start chat
    admin.initiate_chat(
        manager,
        message=f"Create content about: {task}")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_conditional_pipeline("Python generators in programming")

 
