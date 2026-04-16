"""
config/providers.py
-------------------
Defines providers and model lists used in this course.

We only support two providers:
- Groq
- OpenRouter

This file acts as the single source of truth for:
• provider names
• model lists
• environment variables
"""

# -----------------------------
# Provider Identifiers
# -----------------------------

PROVIDER_GROQ = "groq"
PROVIDER_OPENROUTER = "openrouter"

ALL_PROVIDERS = [
    PROVIDER_GROQ,
    PROVIDER_OPENROUTER,
]


# -----------------------------
# Groq Models
# Docs: https://console.groq.com/docs/models
# -----------------------------

GROQ_MODELS = {
    "default": "llama-3.1-8b-instant",      # Recommended default
    "fast": "llama-3.1-8b-instant",               # Fast responses
    "versatile": "llama-3.3-70b-versatile", # Stronger reasoning
}


# -----------------------------
# OpenRouter Free Models
# Docs: https://openrouter.ai/models?q=:free
# -----------------------------

OPENROUTER_MODELS = {
    "default": "meta-llama/llama-3.3-70b-instruct:free",
    "qwen": "qwen/qwen3-8b-instruct:free",
    "mistral": "mistralai/mistral-7b-instruct-v0.3:free",
    "phi": "microsoft/phi-3.5-mini-instruct:free",
}


# -----------------------------
# Approximate Free Tier Limits
# -----------------------------

RATE_LIMITS = {

    PROVIDER_GROQ: {
        "requests_per_minute": 30,
        "tokens_per_minute": 14400,
        "notes": "Free tier. No credit card required.",
    },

    PROVIDER_OPENROUTER: {
        "requests_per_minute": 20,
        "requests_per_day": 200,
        "notes": "Free models only.",
    },

}


# -----------------------------
# Provider Setup URLs
# -----------------------------

PROVIDER_URLS = {

    PROVIDER_GROQ: "https://console.groq.com",
    PROVIDER_OPENROUTER: "https://openrouter.ai/keys",

}


# -----------------------------
# API Key Environment Variables
# -----------------------------

PROVIDER_ENV_KEYS = {

    PROVIDER_GROQ: "GROQ_API_KEY",
    PROVIDER_OPENROUTER: "OPENROUTER_API_KEY",

}


# -----------------------------
# Model Environment Variables
# -----------------------------

PROVIDER_MODEL_ENV_KEYS = {

    PROVIDER_GROQ: "GROQ_MODEL",
    PROVIDER_OPENROUTER: "OPENROUTER_MODEL",

}