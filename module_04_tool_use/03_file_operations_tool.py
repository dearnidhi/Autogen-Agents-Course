from pathlib import Path
import os
from autogen import AssistantAgent, UserProxyAgent, register_function
from dotenv import load_dotenv
load_dotenv()

# =========================
# LLM CONFIG (Groq)
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
# SETUP WORK DIRECTORY
# =========================
BASE_DIR = Path(__file__).parent
WORK_DIR = BASE_DIR / "work_files"
WORK_DIR.mkdir(exist_ok=True)

def safe_path(filename: str) -> Path:
    path = (WORK_DIR / filename).resolve()
    if not str(path).startswith(str(WORK_DIR.resolve())):
        raise ValueError("Invalid file path")
    return path

# =========================
# TOOLS
# =========================
def read_file(filename: str) -> str:
    path = safe_path(filename)
    if not path.exists():
        return f"File not found: {path}"
    return path.read_text()

def write_file(filename: str, content: str) -> str:
    path = safe_path(filename)
    path.write_text(content)
    return "Report written successfully."


# =========================
# MAIN FUNCTION
# =========================
def main():

    assistant = AssistantAgent(
        name="DataAnalyst",
        system_message="""
        You are a data analyst.

        IMPORTANT:
        - You have ONLY TWO tools: read_file and write_file
        - DO NOT invent new tools
        - DO NOT call any tool other than these two

        PROCESS:
        1. Call read_file ONCE
        2. Parse the CSV data YOURSELF (no tool)
        3. Compute:
        - top score
        - average age
        4. Call write_file ONCE with correct result
        5. Reply DONE

        STRICT:
        - No repeated tool calls
        - No empty content
        - No extra tools
        """,
        llm_config=get_config()
    )

    proxy = UserProxyAgent(
        name="Executor",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "DONE" in (msg.get("content") or ""),
    )


    # =========================
    # REGISTER TOOLS
    # =========================
    register_function(
        read_file,
        caller=assistant,
        executor=proxy,
        name="read_file",
        description="Read file content"
    )

    register_function(
        write_file,
        caller=assistant,
        executor=proxy,
        name="write_file",
        description="Write content to file"
    )

    # =========================
    # START CHAT
    # =========================
    proxy.initiate_chat(
        assistant,
        message="Analyse students.csv and create report.txt"
    )

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()

    