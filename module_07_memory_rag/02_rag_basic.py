# ============================================
# SIMPLE RAG (FIXED + SMART RETRIEVAL)
# ============================================

import os
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent

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
        "temperature": 0.5,
    }

# =========================
# KNOWLEDGE BASE
# =========================
knowledge_base = [
    "AutoGen is a framework by Microsoft for building multi-agent AI systems.",
    "AutoGen has two main components: AssistantAgent and UserProxyAgent.",
    "AssistantAgent generates responses using LLM.",
    "UserProxyAgent executes code, tools, and manages user interaction.",
    "GroupChat and GroupChatManager enable multi-agent communication.",
]

# =========================
# IMPROVED RETRIEVAL
# =========================
def retrieve_docs(question):
    question_words = set(question.lower().split())

    scored = [] #store (score, doc) pairs
    for doc in knowledge_base:
        doc_words = set(doc.lower().split())
        score = len(question_words & doc_words) #count how many are common betbeen Q and doc word

        # Boost score if "autogen" present (important keyword)
        if "autogen" in doc.lower():
            score += 1

        scored.append((score, doc))

    # Sort by score
    scored.sort(key=lambda x: x[0], reverse=True)

    # Filter only useful docs
    top_docs = [doc for score, doc in scored if score > 0][:3]

    # Fallback (VERY IMPORTANT)
    if not top_docs:
        return "No relevant context found."

    return "\n".join(top_docs)    

# =========================
# MAIN RAG LOGIC
# =========================
def run_rag():
    print("\n==============================")
    print(" SIMPLE RAG DEMO ")
    print("==============================\n")

    llm_config = get_llm_config()

    # Inject context
    def rag_reply(recipient, messages, sender, config):
        question = messages[-1]["content"] # last user Q from chat history
        context = retrieve_docs(question) # retrieve relavent doc from knowledgebase

        new_prompt = f"""
Use ONLY this context to answer:

{context}

Question: {question}
"""

        messages[-1] = {"role": "user", "content": new_prompt}
        return False, None
     
     
    assistant = AssistantAgent(
        name="RAGAssistant",
        system_message="""
        Answer using the provided context.

        Rules:
        - Be accurate
        - Combine information if needed
        - If nothing useful → say "Not in context"
        - End with DONE
        """,
        llm_config=llm_config,
    )
    # register rag func
    assistant.register_reply(
        trigger=UserProxyAgent,# triggered when user send msg
        reply_func=rag_reply, # func to modify the msg
        position=0, #extract 1st (befor llm)
    )

    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "DONE" in msg.get("content", ""),
    )

# start chat
    user.initiate_chat(
        assistant,
        message="What is AutoGen and its components?",
    )


# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_rag()    