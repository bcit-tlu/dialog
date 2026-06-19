"""Mock LLM client — deterministic responses for testing the graph flow."""

import json
from typing import Any, Optional

from .base_client import BaseLLMClient


class MockClient(BaseLLMClient):
    """Returns pre-canned responses via FakeListChatModel."""

    def __init__(self, model: str = "mock", base_url: Optional[str] = None, **kwargs):
        super().__init__(model, base_url, **kwargs)

    def get_llm(self) -> Any:
        from langchain_core.language_models.fake_chat_models import FakeListChatModel

        chunk_response = json.dumps([
            {"topic": "Mock Topic A", "content": "This is mock knowledge chunk A."},
            {"topic": "Mock Topic B", "content": "This is mock knowledge chunk B."},
        ])

        # FakeListChatModel cycles through responses in order.
        # Current pipeline: extract (no LLM) → chunk (1 LLM call)
        return FakeListChatModel(
            responses=[
                chunk_response,
            ]
        )

    def validate_model(self) -> bool:
        return True
