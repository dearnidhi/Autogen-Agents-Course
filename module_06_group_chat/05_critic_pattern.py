from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import os
from dotenv import load_dotenv

load_dotenv()

# ===== SIMPLE CONFIG =====
llm_config = {
    "config_list": [
        {
            "model": "llama-3.1-8b-instant",
            "api_key": os.getenv("GROQ_API_KEY"),
            "api_type": "groq",
        }
    ],
    "temperature": 0.7,
}


# ===== WRITER =====
writer = AssistantAgent(
    name="Writer",
    system_message="""
Write a short 2 paragraph answer.

If Critic gives feedback → improve it.

If Critic says ESSAY_APPROVED → say WRITING_COMPLETE
""",
    llm_config=llm_config,
)

# ===== CRITIC =====
critic = AssistantAgent(
    name="Critic",
    system_message="""
Give ONLY one improvement.

If improvement needed → CONTINUE
If everything is good → ESSAY_APPROVED
""",
    llm_config=llm_config,
)


# ===== ADMIN =====
admin = UserProxyAgent(
    name="Admin",
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=lambda msg: "WRITING_COMPLETE" in (msg.get("content") or ""),
)

# ===== GROUP CHAT =====
groupchat = GroupChat(
    agents=[writer, critic],
    messages=[],
    max_round=6,
    speaker_selection_method="round_robin",
)


manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config,
    is_termination_msg=lambda msg: "WRITING_COMPLETE" in (msg.get("content") or ""),
)

# ===== RUN =====
admin.initiate_chat(
    manager,
    message="Write about: Why Python is good for beginners",
)

