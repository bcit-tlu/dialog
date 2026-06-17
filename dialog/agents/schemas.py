"""Pydantic schemas for structured LLM outputs and their render helpers.

Each agent that produces structured output has a corresponding schema here.
Render helpers convert parsed Pydantic instances back into markdown / plain
text that the rest of the system can consume unchanged.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Semantic Chunker
# ---------------------------------------------------------------------------


class ChunkOutput(BaseModel):
    """A single atomic knowledge unit extracted from course material."""

    topic: str = Field(description="Short descriptive title for the chunk.")
    content: str = Field(description="Self-contained explanation of one concept, procedure, or fact.")


def render_chunk(chunk: ChunkOutput) -> str:
    return f"**{chunk.topic}**\n\n{chunk.content}"


# ---------------------------------------------------------------------------
# Question Generator
# ---------------------------------------------------------------------------


class QuestionOutput(BaseModel):
    """A single assessment question tied to a knowledge chunk."""

    bloom_level: Literal["recall", "application", "analysis"] = Field(
        description="Bloom's Taxonomy level: recall, application, or analysis.",
    )
    question_text: str = Field(description="The question to ask the learner.")
    answer_text: str = Field(description="A concise correct answer.")


def render_question(q: QuestionOutput) -> str:
    return (
        f"**[{q.bloom_level.capitalize()}]** {q.question_text}\n"
        f"**Answer:** {q.answer_text}"
    )


# ---------------------------------------------------------------------------
# Quality Auditor
# ---------------------------------------------------------------------------


class AuditIssue(BaseModel):
    """A single issue found during quality audit."""

    question_id: str = Field(description="ID of the flagged question.")
    issue: Literal["hallucination", "misclassification", "coverage_gap"] = Field(
        description="Category of the issue.",
    )
    detail: str = Field(description="Explanation of what went wrong.")


class AuditResult(BaseModel):
    """Result of auditing questions against their source chunk."""

    passed: bool = Field(alias="pass", description="True if all questions passed.")
    issues: list[AuditIssue] = Field(default_factory=list)


def render_audit(result: AuditResult) -> str:
    if result.passed:
        return "✅ All questions passed audit."
    lines = ["❌ Issues found:"]
    for issue in result.issues:
        lines.append(f"  - [{issue.issue}] {issue.question_id}: {issue.detail}")
    return "\n".join(lines)
