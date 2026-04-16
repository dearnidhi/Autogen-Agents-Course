# Import required libraries
import os   # os for env
import asyncio
from typing import Annotated
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
# ASYNC TOOLS
# =========================

# async → means this function runs asynchronously (non-blocking)
# symbol → input parameter (e.g., "NVDA", "MSFT")
# Annotated[str, "Stock symbol"] →
#   - str = data type (string)
#   - "Stock symbol" = description (used by AI to understand input)

async def fetch_stock_price(symbol: Annotated[str, "Stock symbol"]) -> str:
    """Simulates fetching stock price"""
    await asyncio.sleep(0.5) # pause this func without blocking entire prog

    price = {"NVDA":875.4, "MSFT":415.2} #DUMMY STOCK DATA
    
    # symbol.upper() → convert input to uppercase (nvda → NVDA)
    # prices.get(...) → safely get value, else return 'Not Found'
    return f"{symbol}: ${price.get(symbol.upper(), 'Not Found')}"

# text → input string (e.g., "Python is great")
# lang → target language (e.g., "Spanish", "French")

async def translate_text(text: str, lang: str) -> str:
    """Simulates translation"""

    # simulate delay (like translation API call)
    await asyncio.sleep(0.3)
  
    translations = {
        "python is great": {
            "spanish": "Python es genial",
            "french": "Python est génial",
            "hindi": "पायथन बहुत शानदार है"
        }
    }
 
    lang_map = {
        "es": "spanish",
        "fr": "french",
        "hi": "hindi"
    }

    text_lower = text.lower()
    lang_full = lang_map.get(lang.lower(), lang.lower())

    if text_lower in translations and lang_full in translations[text_lower]:
        return translations[text_lower][lang_full]

    return f"[No translation available for '{text}' → {lang}]"


# url → input parameter (e.g., "https://python.org")
async def check_website(url: str) -> str:
    """Simulates website status check"""

    # simulate network request delay
    await asyncio.sleep(0.2)

    # returning fake status response
    return f"{url} is UP (200 OK)"

    
# =========================
# SYNC WRAPPERS (WHY NEEDED)
# =========================

# AutoGen tools work with NORMAL (sync) functions only.
# But our actual functions are ASYNC (they use async/await).
# So we create "wrapper functions" to convert async → sync.

# asyncio.run() → runs async function and returns result
# Without this, async function will NOT execute properly.

def stock_sync(symbol: str):
    # Calls async function inside a sync wrapper
    return asyncio.run(fetch_stock_price(symbol))


def translate_sync(text: str, lang: str):
    # Converts async translation function to sync
    # Required because AutoGen cannot directly handle async tools
    return asyncio.run(translate_text(text, lang))


def website_sync(url: str):
    # Runs async website check in sync mode
    return asyncio.run(check_website(url))

# =========================
# MAIN FUNCTION
# =========================
def main():

    assistant = AssistantAgent(
        name="AsyncAgent",
        system_message="""
        Use tools to:
        1. Get stock price
        2. Translate text
        3. Check website

        After all tasks, say ASYNC_DONE
        """,
        llm_config=get_config()
    )

    proxy = UserProxyAgent(
        name="Executor",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: "ASYNC_DONE" in (msg.get("content") or ""),
    )

    
    
# Register tools
    register_function(
        stock_sync,
        caller=assistant,
        executor=proxy,
        name="stock",
        description="Get stock price"
    )

    register_function(
        translate_sync,
        caller=assistant,
        executor=proxy,
        name="translate",
        description="Translate text"
    )

    register_function(
        website_sync,
        caller=assistant,
        executor=proxy,
        name="website",
        description="Check website status"
    )

     # Start conversation
    proxy.initiate_chat(
        assistant,
        message="""
        1. Get NVDA stock price
        2. Translate 'Python is great' to Spanish
        3. Check https://python.org
        """
    )

if __name__ == "__main__":
    main()





