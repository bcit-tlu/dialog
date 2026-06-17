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

        question_response = json.dumps([
            {"bloom_level": "recall", "question_text": "What is mock topic?", "answer_text": "Mock answer."},
            {"bloom_level": "application", "question_text": "How would you apply mock?", "answer_text": "Apply mock."},
            {"bloom_level": "analysis", "question_text": "Analyze mock concept.", "answer_text": "Analysis of mock."},
        ])

        audit_response = json.dumps({"pass": True, "issues": []})

        # FakeListChatModel cycles through responses in order:
        # chunk (1) → questions per chunk (2) → audit per chunk (2)
        return FakeListChatModel(
            responses=[
                chunk_response,
                question_response,
                question_response,
                audit_response,
                audit_response,
            ]
        )

    def validate_model(self) -> bool:
        return True
