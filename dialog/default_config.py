"""Single source of truth for configuration with env-var overlay.

Inspired by TradingAgents' default_config.py — a plain dict that applies
environment variable overrides at import time. No pydantic-settings needed.
"""

import os

_ENV_OVERRIDES = {
    "OLLAMA_BASE_URL":    "ollama_base_url",
    "OLLAMA_API_KEY":     "ollama_api_key",
    "OLLAMA_MODEL":       "ollama_model",
    "MOCK_LLM":           "mock_llm",
    "MAX_CHUNK_TOKENS":   "max_chunk_tokens",
    "MIN_CHUNK_TOKENS":   "min_chunk_tokens",
    "API_HOST":           "api_host",
    "API_PORT":           "api_port",
}


def _coerce(value: str, reference):
    """Coerce env-var string to the type of the existing default value."""
    if isinstance(reference, bool):
        return value.strip().lower() in ("true", "1", "yes", "on")
    if isinstance(reference, int) and not isinstance(reference, bool):
        return int(value)
    if isinstance(reference, float):
        return float(value)
    return value


def _apply_env_overrides(config: dict) -> dict:
    """Apply env vars to the config dict in-place."""
    for env_var, key in _ENV_OVERRIDES.items():
        raw = os.environ.get(env_var)
        if raw is None or raw == "":
            continue
        config[key] = _coerce(raw, config.get(key))
    return config


DEFAULT_CONFIG = _apply_env_overrides({
    # LLM settings — Ollama Cloud via OpenAI-compatible API
    "llm_provider": "openai",
    "ollama_base_url": "https://ollama.com",
    "ollama_api_key": "",
    "ollama_model": "gemma4:31b-cloud",

    # Processing defaults
    "max_chunk_tokens": 800,
    "min_chunk_tokens": 100,

    # Mock mode — run the graph without real LLM calls
    "mock_llm": False,

    # API server
    "api_host": "0.0.0.0",
    "api_port": 8000,
})
