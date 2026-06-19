"""AgentState — the single object that flows through every graph node."""

from __future__ import annotations

from typing import TypedDict


class KnowledgeChunk(TypedDict):
    chunk_id: str
    topic: str
    content: str


class AgentState(TypedDict, total=False):
    # --- inputs ---
    source_path: str          # path to the uploaded file
    raw_text: str             # extracted plain text / markdown

    # --- set by semantic_chunker ---
    knowledge_map: list[KnowledgeChunk]

    # --- meta ---
    error: str | None
