"""
Standalone LLM config — reads this project's own .env file.

Supported providers: groq, openrouter, cerebras.
Set DEFAULT_PROVIDER and the matching API key in .env.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load the .env that sits next to this file
load_dotenv(Path(__file__).parent / ".env")

# provider -> (env key name, env model name, default model, optional base_url)
PROVIDERS = {
    "groq": ("GROQ_API_KEY", "GROQ_MODEL", "llama-3.3-70b-versatile", None),
    "openrouter": ("OPENROUTER_API_KEY", "OPENROUTER_MODEL", "google/gemma-4-31b-it:free",
                   "https://openrouter.ai/api/v1"),
    "cerebras": ("CEREBRAS_API_KEY", "CEREBRAS_MODEL", "gpt-oss-120b", None),
}


def get_llm_config(provider=None, temperature=0.7, seed=42):
    """Build an AutoGen llm_config from .env values."""
    provider = provider or os.getenv("DEFAULT_PROVIDER", "groq")
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")

    key_name, model_name, default_model, base_url = PROVIDERS[provider]
    api_key = os.getenv(key_name)
    if not api_key:
        raise EnvironmentError(f"{key_name} is missing. Add it to .env.")

    cfg = {"model": os.getenv(model_name) or default_model, "api_key": api_key}
    if base_url:
        cfg["base_url"] = base_url
    else:
        cfg["api_type"] = provider

    return {"config_list": [cfg], "temperature": temperature, "seed": seed}


def print_current_config():
    """Print the active provider and model (with a masked key)."""
    provider = os.getenv("DEFAULT_PROVIDER", "groq")
    try:
        cfg = get_llm_config(provider)["config_list"][0]
        key = cfg["api_key"]
        print(f"Provider: {provider}")
        print(f"Model   : {cfg['model']}")
        print(f"API Key : {key[:6]}...{key[-4:]}")
    except Exception as e:
        print(f"Config error: {e}")
