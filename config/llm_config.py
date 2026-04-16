"""
config/llm_config.py
--------------------
Central LLM configuration manager for this course.

Supported providers:
• Groq
• OpenRouter

Usage:

from config.llm_config import get_llm_config

llm_config = get_llm_config()

agent = AssistantAgent(
    name="assistant",
    llm_config=llm_config
)
"""

import os
import sys  

from typing import Optional, Dict, Any, List
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from .providers import (
    PROVIDER_GROQ,
    PROVIDER_OPENROUTER,
    GROQ_MODELS,
    OPENROUTER_MODELS,
    PROVIDER_ENV_KEYS,
    PROVIDER_MODEL_ENV_KEYS,
)

load_dotenv()


class LLMConfigBuilder:
    """Builds AutoGen-compatible llm_config."""

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or os.getenv("DEFAULT_PROVIDER", PROVIDER_GROQ)

    def _get_api_key(self) -> str:
        env_var = PROVIDER_ENV_KEYS.get(self.provider)

        if not env_var:
            raise ValueError(f"Unknown provider: {self.provider}")

        api_key = os.getenv(env_var)

        if not api_key:
            raise EnvironmentError(
                f"{env_var} is not set. Add it to your .env file."
            )

        return api_key

    def _get_model(self, model_map: dict) -> str:
        env_var = PROVIDER_MODEL_ENV_KEYS.get(self.provider)
        env_model = os.getenv(env_var, "") if env_var else ""

        return env_model or model_map["default"]

    def build_config_list(self) -> List[Dict[str, Any]]:

        if self.provider == PROVIDER_GROQ:
            return self._build_groq_config()

        if self.provider == PROVIDER_OPENROUTER:
            return self._build_openrouter_config()

        raise ValueError(f"Unsupported provider: {self.provider}")

    def _build_groq_config(self) -> List[Dict[str, Any]]:

        api_key = self._get_api_key()
        model = self._get_model(GROQ_MODELS)

        return [
            {
                "model": model,
                "api_key": api_key,
                "api_type": "groq",
            }
        ]

    def _build_openrouter_config(self) -> List[Dict[str, Any]]:

        api_key = self._get_api_key()
        model = self._get_model(OPENROUTER_MODELS)

        return [
            {
                "model": model,
                "api_key": api_key,
                "base_url": "https://openrouter.ai/api/v1",
            }
        ]

    def build_llm_config(
        self,
        temperature: float = 0.7,
        seed: Optional[int] = 42,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:

        config_list = self.build_config_list()

        llm_config: Dict[str, Any] = {
            "config_list": config_list,
            "temperature": temperature,
        }

        if seed is not None:
            llm_config["seed"] = seed

        if max_tokens is not None:
            llm_config["max_tokens"] = max_tokens

        return llm_config


def get_llm_config(
    provider: Optional[str] = None,
    temperature: float = 0.7,
    seed: Optional[int] = 42,
) -> Dict[str, Any]:
    """
    Main function used across the course.
    """

    return LLMConfigBuilder(provider).build_llm_config(
        temperature=temperature,
        seed=seed,
    )


def print_current_config() -> None:
    """
    Prints active provider and model.
    """

    provider = os.getenv("DEFAULT_PROVIDER", PROVIDER_GROQ)

    try:
        config = get_llm_config(provider)
        cfg = config["config_list"][0]

        model = cfg["model"]
        key = cfg["api_key"]

        masked = key[:6] + "..." + key[-4:]

        print(f"Provider: {provider}")
        print(f"Model: {model}")
        print(f"API Key: {masked}")

    except Exception as e:
        print(f"Config error: {e}")


from config.llm_config import get_llm_config, print_current_config

if __name__ == "__main__":
    # Test the configuration
    print_current_config()
    
    # Get config for different providers
    groq_config = get_llm_config(provider="groq")
    print("\nGroq config:", groq_config.keys())
    
    openrouter_config = get_llm_config(provider="openrouter")
    print("OpenRouter config:", openrouter_config.keys()) 
       