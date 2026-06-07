"""Reads the Groq API key from .env and builds the AutoGen config."""

import os
from pathlib import Path
from dotenv import load_dotenv

# load the API key from this folder's .env
load_dotenv(Path(__file__).parent / ".env")


def get_llm_config(temperature=0.7):
    """Return the AutoGen llm_config using the Groq key + model from .env."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY missing in .env")

    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    return {
        "config_list": [{"model": model, "api_key": api_key, "api_type": "groq"}],
        "temperature": temperature,
    }
