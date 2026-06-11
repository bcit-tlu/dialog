"""LLM factory — returns either a real ChatOpenAI or a mock for testing."""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel

from processor.config import settings


def get_llm() -> BaseChatModel:
    if settings.mock_llm:
        return _mock_llm()

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        base_url=f"{settings.ollama_base_url}/v1",
        api_key=settings.ollama_api_key,
        model=settings.ollama_model,
        temperature=0,
    )


# ---------------------------------------------------------------------------
# Mock LLM — deterministic responses for testing the graph flow
# ---------------------------------------------------------------------------

def _mock_llm() -> BaseChatModel:
    import json

    from langchain_core.messages import AIMessage
    from langchain_core.language_models.fake import FakeListChatModel

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
            question_response,  # called once per chunk
            question_response,
            audit_response,     # called once per chunk
            audit_response,
        ]
    )
