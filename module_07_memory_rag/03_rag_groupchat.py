# ============================================
# RAG GROUPCHAT (CLEAN + PRACTICAL)
# ============================================

import os
from pathlib import Path
from dotenv import load_dotenv

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

load_dotenv()

# =========================
# LLM CONFIG (GROQ)
# =========================
def get_llm_config():
    return {
        "config_list": [
            {
                "model": "llama-3.1-8b-instant",
                "api_key": os.getenv("GROQ_API_KEY"),
                "api_type": "groq",
            }
        ],
        "temperature": 0.4,
    }


# =========================
# LOAD DOCUMENTS
# =========================
BASE_DIR = Path(__file__).resolve().parent #get dir where python file located
DOCS_DIR = BASE_DIR / "rag_docs" #

def load_knowledge_base():
    docs = []

    for file in DOCS_DIR.glob("*.txt"):
        content = file.read_text(encoding="utf-8")

        # Split into chunks (paragraphs)
        chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 40]

        for i, chunk in enumerate(chunks):
            docs.append({
                "id": f"{file.stem}_{i}",
                "text": chunk
            })

    return docs

# =========================
# SIMPLE RETRIEVAL
# =========================
def retrieve_docs(query, docs, top_k=3):
    query_words = set(query.lower().split())
    scored = []

    for doc in docs:
        doc_words = set(doc["text"].lower().split())

        # basic keyword match score
        score = len(query_words & doc_words)

        scored.append((score, doc["text"]))

    # sort highest score first
    scored.sort(key=lambda x: x[0], reverse=True)

    # take top results
    top_docs = [text for score, text in scored if score > 0][:top_k]

    if not top_docs:
        return "No relevant context found."

    return "\n\n---\n\n".join(top_docs)    

# =========================
# MAIN GROUPCHAT
# =========================
def run_rag_groupchat(question):
    print("\n==============================")
    print(" RAG GROUPCHAT DEMO ")
    print("==============================\n")

    docs = load_knowledge_base()

    if not docs:
        print("No documents found inside rag_docs folder.")
        return

    print(f"Loaded {len(docs)} document chunks\n")

    llm_config = get_llm_config()

    # retrieve context once
    context = retrieve_docs(question, docs)

    # -------------------------
    # AGENTS
    # -------------------------
    knowledge_agent = AssistantAgent(
        name="KnowledgeAgent",
        system_message=f"""
        Use ONLY this context:

        {context}

        Rules:
        - Give useful info from context
        - If nothing found → say "Not in context"
        - Do NOT send empty response
        - End with: KNOWLEDGE_DONE
        """,
        llm_config=llm_config,
    )

    analyst_agent = AssistantAgent(
        name="AnalystAgent",
        system_message="""
        You analyze the answer from KnowledgeAgent.

        - Extract key points
        - Explain simply
        - Add clarity

        End with DONE
        """,
        llm_config=llm_config,
    )

    summary_agent = AssistantAgent(
        name="SummaryAgent",
        system_message="""
        You create the final answer.

        Rules:
        - Give final structured answer
        - Be clear and complete
        - End STRICTLY with: FINAL_DONE
        """,
        llm_config=llm_config,
    )

    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "FINAL_DONE" in msg.get("content", "")
    )

    # -------------------------
    # GROUPCHAT
    # -------------------------
    groupchat = GroupChat(
        agents=[user, knowledge_agent, analyst_agent, summary_agent],
        messages=[],
        max_round=4,
        speaker_selection_method="round_robin",

    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        is_termination_msg=lambda msg: "FINAL_DONE" in msg.get("content", "")

    )

    user.initiate_chat(
        manager,
        message=question,
    )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_rag_groupchat("What is AutoGen and its components?")