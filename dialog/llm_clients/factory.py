"""LLM client factory — dispatches to the correct provider client.

Modules are imported lazily so that importing this factory does not
pull in heavy LLM SDKs or fail when API keys are absent.
"""

from typing import Optional

from .base_client import BaseLLMClient


def create_llm_client(
    provider: str = "openai",
    model: str = "gemma4:31b-cloud",
    base_url: Optional[str] = None,
    mock: bool = False,
    **kwargs,
) -> BaseLLMClient:
    """Create an LLM client for the specified provider.

    Args:
        provider: LLM provider name ("openai", "mock", etc.)
        model: Model name / identifier
        base_url: Optional base URL for the API endpoint
        mock: If True, return a MockClient regardless of provider
        **kwargs: Additional provider-specific arguments (api_key, temperature, ...)

    Returns:
        Configured BaseLLMClient instance
    """
    if mock:
        from .mock_client import MockClient
        return MockClient(model, base_url, **kwargs)

    provider_lower = provider.lower()

    if provider_lower in ("openai", "ollama"):
        from .openai_client import OpenAIClient
        return OpenAIClient(model, base_url, **kwargs)

    raise ValueError(f"Unsupported LLM provider: {provider}")
