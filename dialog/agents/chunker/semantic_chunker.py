"""Semantic Chunker agent — splits text into Atomic Knowledge Units."""

from __future__ import annotations

import json
import uuid

from dialog.agents.utils.agent_states import AgentState, KnowledgeChunk

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


def create_semantic_chunker(llm):
    """Factory: create a semantic chunker node that captures the given LLM."""

    def semantic_chunker_node(state: AgentState) -> dict:
        """Chunk raw_text into knowledge_map entries."""
        raw = state.get("raw_text", "")

        response = llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw},
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

    return semantic_chunker_node
