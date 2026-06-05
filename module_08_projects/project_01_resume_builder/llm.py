"""Standalone LLM config — reads this folder's own .env. No shared config needed."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "sample_input" / ".env")

# provider -> (env key, env model, default model, base_url or None)
PROVIDERS = {
    "groq": ("GROQ_API_KEY", "GROQ_MODEL", "llama-3.1-8b-instant", None),
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
