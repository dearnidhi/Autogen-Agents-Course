"""
StateFlow = fixed workflow using states (like steps)

Flow:
ANALYZE → CRITIQUE → (REVISE if needed) → APPROVE → DONE
"""

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from dotenv import load_dotenv
import os

load_dotenv()

STATE_ANALYZE = "ANALYZE"
STATE_CRITIQUE = "CRITIQUE"
STATE_REVISE = "REVISE"
STATE_APPROVE = "APPROVE"
STATE_DONE = "DONE"



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

def run_pipeline(document:str):
    llm_config = get_config()

    
    # =========================
    # AGENTS
    # =========================
    analyzer = AssistantAgent(
        name="Analyzer",
        system_message="Analyze document. End with ANALYSIS_DONE",
        llm_config=llm_config
    )

    critic = AssistantAgent(
        name="Critic",
        system_message="""
        Check issues.
        If problems → write NEEDS_REVISION
        Else → NO_REVISION_NEEDED
        End with CRITIQUE_DONE
        """,
        llm_config=llm_config
    )

    revisor = AssistantAgent(
        name="Revisor",
        system_message="""
        Fix the document based on critique.

        IMPORTANT:
        - Do NOT write plan
        - Do NOT write steps
        - ONLY give final improved version

        End STRICTLY with: REVISION_DONE
        """,
        llm_config=llm_config
    )

    approver = AssistantAgent(
        name="Approver",
        system_message="""
        Give final decision.

        ONLY output:
        APPROVED or REJECTED

        End STRICTLY with: APPROVAL_DONE
        """,
        llm_config=llm_config
    )

    admin = UserProxyAgent(
        name="Admin",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "APPROVAL_DONE" in (msg.get("content") or ""),
    )
    # =========================
    # STATE TRACKER
    # =========================
    state = {"current":STATE_ANALYZE} # start with analyze

    # =========================
    # SELECTOR 
    # =========================
    def selector(last_speaker, groupchat: GroupChat):

        messages = groupchat.messages   # get all chat messages
        last_msg = messages[-1].get("content", "") if messages else ""  
        # get last message content (used to decide next agent)

        # -------------------------
        # STEP 1 → ANALYZE
        # -------------------------
        if state["current"] == STATE_ANALYZE:
            state["current"] = STATE_CRITIQUE  
            # move next step → CRITIQUE

            return analyzer  
            # send task to Analyzer

        # -------------------------
        # STEP 2 → CRITIQUE
        # -------------------------
        elif state["current"] == STATE_CRITIQUE:

            # First time → send to Critic
            if last_speaker.name != "Critic":
                return critic  
                # wait for Critic to respond

            # After Critic speaks → check result

            # IF critic says revision needed
            if "NEEDS_REVISION" in last_msg:
                state["current"] = STATE_REVISE  
                # go to REVISE step
                print("→ Going to REVISE")
                return revisor


            # ELSE no issues
            else:
                state["current"] = STATE_APPROVE  
                # skip revise → go to APPROVE
                print("→ No issues, go to APPROVE")
                return approver    

        # -------------------------
        # STEP 3 → REVISE
        # -------------------------
        elif state["current"] == STATE_REVISE:
            if last_speaker.name != "Revisor":
                return revisor  
            state["current"] = STATE_APPROVE  
            # after fixing → go to APPROVE

            return approver  
            # send to Revisor         

        # -------------------------
        # STEP 4 → APPROVE
        # -------------------------

        elif state["current"] == STATE_APPROVE:

            if last_speaker.name != "Approver":
                return approver

            state["current"] = STATE_DONE
            return admin  
        # -------------------------
        # END → STOP
        # -------------------------
        return admin  
        # safe exit (end chat)


    # =========================
    # GROUP CHAT
    # =========================
    groupchat = GroupChat(
        agents=[admin, analyzer, critic, revisor, approver],
        messages= [],
        max_round=8,
        speaker_selection_method=selector

    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: "APPROVAL_DONE" in (msg.get("content") or ""),
    )

    # Start chat
    admin.initiate_chat(manager, message=f"Check this:\n{document}")

    

if __name__ == "__main__":
    doc = "Python is good. People use it. It is nice."
    run_pipeline(doc)

     