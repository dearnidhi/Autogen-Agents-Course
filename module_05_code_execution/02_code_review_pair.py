import os
import re
from pathlib import Path
from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
os.environ["AUTOGEN_USE_DOCKER"] = "0"

# Load API key
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
WORK_DIR = BASE_DIR / "workspace"
WORK_DIR.mkdir(exist_ok=True)    

executor =  LocalCommandLineCodeExecutor(
    work_dir= WORK_DIR,
    timeout =30
)

writer = AssistantAgent(
    name="Writer",
    system_message="""
      Write clean Python code.
    - include type hints
    - include docstring
    - handle edge cases
    - wrap in ```python```
    When reviewer says APPROVED → reply CODE_APPROVED
    """,

    llm_config=get_config()
)

# =========================
# REVIEWER
# =========================
reviewer = AssistantAgent(
    name="Reviewer",
    system_message="""
Review code strictly.
If correct → say APPROVED
Else → ask for fix
""",
    llm_config=get_config(),
)


runner = UserProxyAgent(
    name="Runner",
    human_input_mode="NEVER",
    code_execution_config={"executor": executor},
)

# =========================
# MAIN PIPELINE
# =========================
def main():
    task = """
Write a function word_frequency(text: str) -> dict
- ignore case
- remove punctuation
- return dict
- include example usage
"""

 # STEP 1: Writer generates Python code based on the task
    response = writer.generate_reply(
        messages=[{"role": "user", "content": task}]
    )
    code_msg = response["content"]  # Extract the generated code text

    # Print the raw output from the Writer agent
    print("\n===== WRITER OUTPUT =====\n")
    print(code_msg)

    # STEP 2: Reviewer checks the generated code
    review = reviewer.generate_reply(
        messages=[{"role": "user", "content": code_msg}]
    )

    # Print review feedback
    print("\n===== REVIEWER OUTPUT =====\n")
    print(review["content"])

    # If reviewer does not approve, stop execution
    if "APPROVED" not in review["content"]:
        print("❌ Rejected:\n", review["content"])
        return

    print("✅ Approved\n")

    
    # STEP 3: Extract Python code from ```python ... ``` block
    match = re.search(r"```python(.*?)```", code_msg, re.DOTALL)
    
    # If no code block found, stop
    if not match:
        print("❌ No code block found")
        return

    # Clean extracted code
    code = match.group(1).strip()

    # STEP 4: Execute the extracted code using the runner (executor)
    result = runner.run_code(code)

    # Print execution result (output of the generated code)
    print("\n===== EXECUTION OUTPUT =====\n")
    print(result)
    
    
# =========================
# START
# =========================
if __name__ == "__main__":
    main()