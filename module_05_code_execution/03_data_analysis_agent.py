"""
Clean Data Analysis Agent (Groq + Fixed Logic)
Run: python 03_data_analysis_agent.py

workspace/ → where files & execution happen
sales.csv → sample dataset
Agent → AI that writes analysis code
Runner → executes that code
Groq API → gives fast LLM response
"""
import csv
import os
from pathlib import Path
from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv

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
        "temperature": 0.2,
    }


# ------------------ Setup ------------------

# Creating a folder named 'workspace'
WORK_DIR = Path("workspace")

# This will create the folder automatically if it doesn't exist
WORK_DIR.mkdir(exist_ok=True)

# ------------------ Sample CSV ------------------

def create_sample_csv():
    # Sample data in CSV format (as string)
    data = """date,product,region,units_sold,revenue,customer_rating
2024-01-15,Laptop Pro,North,45,58500,4.2
2024-01-15,Phone X,South,120,96000,4.7
2024-01-16,Laptop Pro,East,38,49400,4.0
2024-01-16,Tablet Y,West,89,62300,4.5
2024-01-17,Phone X,North,95,76000,4.8
2024-01-17,Laptop Pro,South,52,67600,4.3

"""
    # Creating file path inside workspace folder
    file_path = WORK_DIR / "sales.csv"

    # Writing the data into CSV file
    file_path.write_text(data)

    # Returning file path
    return file_path

# ------------------ AGENT ------------------
def run_agent(csv_file):
    executor =  LocalCommandLineCodeExecutor(work_dir= WORK_DIR)

    # AI Analyst agent

    analyst = AssistantAgent(
    name="Analyst",
    system_message="""Write SIMPLE Python code.

RULES:
- Use csv.DictReader
- Read file ONLY once

COLUMNS:
date, product, region, units_sold, revenue, customer_rating

TYPE:
- revenue → float
- units_sold → int
- customer_rating → float

CALCULATE:

1. Revenue by product

2. Units by region

3. Avg rating by product:
   - Use TWO dicts: rating_sum, rating_count
   - Do NOT read file again
   - avg = sum / count

4. Best day by TOTAL revenue:
   - Sum revenue per date
   - Then find max

Keep code short.
Print clean output.
End with print("DONE")""",

    llm_config=get_config()
)

# runner execute the code written by analyst
    runner = UserProxyAgent(
        name="Runner",
        human_input_mode="NEVER",
        code_execution_config={"executor": executor, "capture_output": True},
        max_consecutive_auto_reply=5,
        is_termination_msg=lambda msg: msg.get("content", "").strip().endswith("DONE"),

    )

    runner.initiate_chat(
        analyst,
       # Task given to AI
        message=f"""
        Analyze '{csv_file.name}' and give:

        - Revenue by product
        - Units by region
        - Avg rating by product
        - Best day by revenue
        """)

        
if __name__ == "__main__":

    # Create CSV file
    file = create_sample_csv()

    # Show file path
    print("CSV ready:", file)

    # Run AI analysis
    run_agent(file)

    