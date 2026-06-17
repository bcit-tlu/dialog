"""Test the full graph flow using the mock LLM — no tokens spent."""

import os
import tempfile

from dialog.graph import CourseProcessorGraph

# Force mock mode for tests
os.environ["MOCK_LLM"] = "true"

# Re-import config after setting env var so the override takes effect
from dialog.default_config import DEFAULT_CONFIG

_config = {**DEFAULT_CONFIG, "mock_llm": True}


def _run_pipeline(text: str) -> dict:
    """Helper: write text to a temp file and run the pipeline."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(text)
        tmp_path = f.name

    try:
        graph = CourseProcessorGraph(config=_config)
        return graph.process(tmp_path)
    finally:
        os.unlink(tmp_path)


def test_mock_pipeline_runs_end_to_end():
    """The graph should complete all nodes and produce structured output."""
    result = _run_pipeline("Sepsis is a life-threatening condition caused by infection.")

    assert len(result["knowledge_map"]) > 0, "Should produce at least one chunk"
    assert len(result["question_bank"]) > 0, "Should produce at least one question"
    assert result["review_status"] in ("approved", "needs_review")


def test_mock_questions_have_bloom_levels():
    result = _run_pipeline("Mock nursing content for testing purposes.")

    bloom_levels = {q["bloom_level"] for q in result["question_bank"]}
    assert "recall" in bloom_levels
    assert "application" in bloom_levels
    assert "analysis" in bloom_levels
