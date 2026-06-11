"""Node 2 — Semantic Chunker: Split text into Atomic Knowledge Units."""

from __future__ import annotations

import uuid

from processor.llm import get_llm
from processor.state import AgentState, KnowledgeChunk

SYSTEM_PROMPT = """\
You are a medical content analyst. Given the full text of a course module,
split the text into self-contained "Atomic Knowledge Units".

Each unit must:
1. Cover exactly ONE concept, procedure, or fact.
2. Be understandable without the surrounding context.
3. Have a short descriptive topic title.

Return your answer as a JSON array of objects with keys "topic" and "content".
Example:
[
  {{"topic": "Sepsis Definition", "content": "Sepsis is a life-threatening..."}},
  {{"topic": "qSOFA Criteria", "content": "The quick SOFA score..."}}
]

Return ONLY the JSON array. No markdown fences, no explanation.
"""


def semantic_chunker(state: AgentState) -> dict:
    """Chunk raw_text into knowledge_map entries."""
    import json

    llm = get_llm()
    raw = state.get("raw_text", "")

    user_msg = raw

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ])

    try:
        chunks_raw = json.loads(response.content.strip())
    except json.JSONDecodeError:
        return {"knowledge_map": [], "error": "Chunker returned invalid JSON"}

    knowledge_map: list[KnowledgeChunk] = []
    for item in chunks_raw:
        knowledge_map.append(
            KnowledgeChunk(
                chunk_id=str(uuid.uuid4())[:8],
                topic=item.get("topic", "Untitled"),
                content=item.get("content", ""),
            )
        )

    return {"knowledge_map": knowledge_map}
