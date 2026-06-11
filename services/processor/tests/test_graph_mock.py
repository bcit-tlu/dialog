"""Test the full graph flow using the mock LLM — no tokens spent."""

import os
import tempfile

os.environ["MOCK_LLM"] = "true"

from processor.graph import compile_graph


def test_mock_pipeline_runs_end_to_end():
    """The graph should complete all nodes and produce structured output."""
    # Create a tiny temp file to act as the "uploaded document"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Sepsis is a life-threatening condition caused by infection.")
        tmp_path = f.name

    try:
        graph = compile_graph()
        result = graph.invoke({"source_path": tmp_path})
    finally:
        os.unlink(tmp_path)

    assert result["department"], "Department should be set"
    assert len(result["knowledge_map"]) > 0, "Should produce at least one chunk"
    assert len(result["question_bank"]) > 0, "Should produce at least one question"
    assert result["review_status"] in ("approved", "needs_review")


def test_mock_questions_have_bloom_levels():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Mock nursing content for testing purposes.")
        tmp_path = f.name

    try:
        graph = compile_graph()
        result = graph.invoke({"source_path": tmp_path})
    finally:
        os.unlink(tmp_path)

    bloom_levels = {q["bloom_level"] for q in result["question_bank"]}
    assert "recall" in bloom_levels
    assert "application" in bloom_levels
    assert "analysis" in bloom_levels
