
import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# Load API key
from dotenv import load_dotenv
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

# =========================
# ROUND ROBIN CHAT
# =========================
def run_debate(topic):

    print("\n===== ROUND ROBIN CHAT =====\n")
    
    # LLM config load
    llm_config = get_config()


    # 1. Optimist (positive side)
   
    optimist = AssistantAgent(
        name="Optimist",
        system_message="Support the topic. Be positive. Keep it short.",
        llm_config=llm_config
    )

    # 2. Pessimist (negative side)
    pessimist = AssistantAgent(
        name="Pessimist",
        system_message="Oppose the topic. Focus on risks. Keep it short.",
        llm_config=llm_config
    )

    # 3. Realist (balanced)
    realist = AssistantAgent(
        name="Realist",
        system_message="Give a balanced view of both sides.",
        llm_config=llm_config
    )

    # 4. Moderator (final summary)
    moderator = AssistantAgent(
        name="Moderator",
        system_message="Summarize all views and give final conclusion. End with DONE.",
        llm_config=llm_config
    )

    # Admin (controls chat)
   
    admin = UserProxyAgent(
        name="Admin",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "DONE" in (msg.get("content") or ""),
    )

   
    # GroupChat (FIXED ORDER)
  
    groupchat = GroupChat(
        agents=[optimist,pessimist, realist, moderator ],
        messages= [],
        max_round=6,
        speaker_selection_method="round_robin" #MAIN CONCEPT

    )
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: "DONE" in (msg.get("content") or ""),
    )

    # Start chat
    admin.initiate_chat(
        manager,
        message=f"Debate this topic: {topic}" )


# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_debate("AI will replace junior developers")
