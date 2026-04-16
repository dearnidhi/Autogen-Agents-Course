"""
Simple Math Agent using AutoGen (Groq/OpenRouter)
Tools: Calculator, Stats, Unit Conversion
"""

# Import required libraries
import os, math, statistics  # os for env, math for calculations, statistics for stats
from dotenv import load_dotenv  # loads environment variables from .env file
from autogen import AssistantAgent, UserProxyAgent, register_function  # AutoGen core classes

# Load API keys from .env file
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
# TOOLS
# =========================

# Tool 1: Safe math evaluator
def calculate(expression: str)->str:
    """
    This function evaluates a mathematical expression given as a string.

    Parameters:
    expression (str): A math expression in string format
                      Example: "2+2", "sqrt(16)", "pi*5**2"

    Returns:
    str: Result of the calculation OR error message
    """
    try: 
        expression = expression.replace("^", "**")
        #2^3(wrong in pythin)-> 2**3(correct)
        #eval()=> convert str epression into actual python code and execute it
        #eg;- "2+2"->4

        result = eval(
            expression,
            {"__builtins__":None}, # disable all bulit in fun for safety
            {"sqrt": math.sqrt,
            "pi":math.pi
            }
        )

  # Return the original expression along with its result
        return f"{expression} = {result}"

    except Exception as e:
        # If any error occurs (invalid input, syntax issue, etc.)
        # return a safe error message instead of crashing
        return f"Error: {e}"


# Tool 2: Statistics summary
def stats_summary(numbers: str) -> str:
    nums = [float(x) for x in numbers.split(",")]  # convert input string to list of numbers
    return (
        f"Mean: {statistics.mean(nums)}\n"     # calculate mean
        f"Median: {statistics.median(nums)}\n" # calculate median
        f"Std: {statistics.stdev(nums)}"       # calculate standard deviation
    )    


# Tool 3: Unit conversion
def convert_units(value: float, from_unit: str, to_unit: str) -> str:   
    """
    Converts basic units between km→miles and kg→lbs.

    Parameters:
    - value (float): numeric value to convert
    - from_unit (str): unit you are converting FROM (e.g. 'km', 'kg')
    - to_unit (str): unit you are converting TO (e.g. 'miles', 'lbs')

    Returns:
    - str: formatted conversion result OR error message
    """     
    
  # Case 1: Convert kilometers to miles
    # 1 km ≈ 0.621 miles
    if from_unit == "km" and to_unit == "miles":
        converted = value * 0.621  # apply conversion formula
        return f"{value} km = {converted} miles"  # return formatted result


    # Case 2: Convert kilograms to pounds
    # 1 kg ≈ 2.204 lbs
    if from_unit == "kg" and to_unit == "lbs":
        converted = value * 2.204  # apply conversion formula
        return f"{value} kg = {converted} lbs"  # return formatted result

    # If conversion pair is not supported
    return "Conversion not supported"    
    
# =========================
# MAIN FUNCTION
# =========================
def run():
    
    assistant = AssistantAgent(
        name="MathAgent",
        system_message="""
        You are a math expert.

        RULES:
        - Always use tools
        - Do not calculate manually
        - Solve step by step
        - End with MATH_DONE
        """,
        llm_config=get_config()
    )    

    proxy = UserProxyAgent(
        name="Executor",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "MATH_DONE" in (msg.get("content") or ""),
    )

    # =========================
    # REGISTER TOOLS
    # =========================
    register_function(
        stats_summary,
        caller=assistant,
        executor=proxy,
        name="stats",
        description="stats"
    )

    register_function(
        calculate,
        caller=assistant,
        executor=proxy,
        name="calculate",
        description="Math cal"
    )

    register_function(
        convert_units,
        caller=assistant,
        executor=proxy,
        name="convert",
        description="Unit convert"
    )
    # =========================
    # START CHAT
    # =========================
    proxy.initiate_chat(
        assistant,
        message=
        """
1. Calculate pi * 7^2
2. Stats: 45,67,89,23,56,78,34,91
3. Convert 100 km to miles and 75 kg to lbs
"""
    )

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run()