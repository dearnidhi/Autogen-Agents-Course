"""
config/validator.py
-------------------
Simple configuration validator for this course.

Checks whether Groq or OpenRouter API keys are configured correctly.

Run this command to test your setup:

python -m config.validator
"""
import os
import sys
from typing import Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .providers import (
    PROVIDER_GROQ,
    PROVIDER_OPENROUTER,
    PROVIDER_ENV_KEYS,
    PROVIDER_URLS,
)

# Only two providers used in this course
COURSE_PROVIDERS = [PROVIDER_GROQ, PROVIDER_OPENROUTER]

def validate_provider(provider: str) -> Tuple[bool, str]:
    """
    Checks if a provider's API key exists in the .env file.
    No API call is made here.
    """
    # Get environment variable name
    # Example: GROQ_API_KEY
    env_var = PROVIDER_ENV_KEYS.get(provider)

    if not env_var:
        return False, f"Unknown provider: {provider}"

    # Read API key from environment
    value = os.getenv(env_var, "")

    # Case 1: Key missing
    if not value:
        return False, f"NOT SET — Add {env_var} to your .env file"

    # Case 2: Placeholder value
    if value.endswith("_here") or value == "your_key_here":
        url = PROVIDER_URLS.get(provider, "")
        return False, f"PLACEHOLDER — Get a real key at {url}"
    # Case 3: Suspiciously short key
    if len(value) < 10:
        return False, f"TOO SHORT — Key may be invalid"
    # If everything looks fine
    return True, f"OK (length: {len(value)} chars)"

def run_validation() -> bool:
    """
    Runs validation for Groq and OpenRouter.
    """
    print()
    print("=" * 50)
    print(" AutoGen Course — Config Validator")
    print("=" * 50)

    default_provider = os.getenv("DEFAULT_PROVIDER", "groq")
    print(f"DEFAULT_PROVIDER: {default_provider}")
    print()
    any_valid = False

    for provider in COURSE_PROVIDERS:
        # Validate each provider
        is_valid, message = validate_provider(provider)

        status = "[OK]" if is_valid else "[SKIP]"
        env_var = PROVIDER_ENV_KEYS.get(provider, "?")

        print(f"{status} {provider:<12} {env_var}: {message}")

        if is_valid:
            any_valid = True
    print()
    print("-" * 50)

    if any_valid:
        print("Configuration looks good.")
    else:
        print("No valid providers found.")
        print()
        print("Fix:")
        print("1. Open your .env file")
        print("2. Add GROQ_API_KEY or OPENROUTER_API_KEY")
        print()
        print("Get a free Groq key here:")
        print("https://console.groq.com")

    print("=" * 50)
    print()
    return any_valid

if __name__ == "__main__":

    # Run validator from terminal
    # Example: python -m config.validator
    ready = run_validation()

    # Exit with success or failure
    sys.exit(0 if ready else 1)