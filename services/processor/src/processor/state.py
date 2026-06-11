"""AgentState — the single object that flows through every graph node."""

from __future__ import annotations

from typing import TypedDict


class KnowledgeChunk(TypedDict):
    chunk_id: str
    topic: str
    content: str


class Question(TypedDict):
    question_id: str
    chunk_id: str
    bloom_level: str          # recall | application | analysis
    question_text: str
    answer_text: str


class AuditFlag(TypedDict):
    chunk_id: str
    issue: str                # e.g. "hallucination", "coverage_gap"
    detail: str


class AgentState(TypedDict, total=False):
    # --- inputs ---
    source_path: str          # path to the uploaded file
    raw_text: str             # extracted plain text / markdown

    # --- set by classify_dept (future) ---
    # department: str

    # --- set by semantic_chunker ---
    knowledge_map: list[KnowledgeChunk]

    # --- set by generate_questions ---
    question_bank: list[Question]

    # --- set by audit_content ---
    audit_flags: list[AuditFlag]
    review_status: str        # "pending" | "approved" | "needs_review"

    # --- meta ---
    error: str | None
