"""Node 4 — Quality Auditor: Cross-reference questions against source chunks."""

from __future__ import annotations

import json

from processor.llm import get_llm
from processor.state import AgentState, AuditFlag

SYSTEM_PROMPT = """\
You are a medical content auditor. You will receive:
1. A knowledge chunk (topic + content).
2. A list of questions generated from that chunk.

For each question, verify:
- The answer is fully supported by the chunk content (no hallucination).
- The question is clinically relevant and correctly categorized by Bloom's level.

If ALL questions pass, return: {{"pass": true, "issues": []}}
If any fail, return: {{"pass": false, "issues": [
  {{"question_id": "...", "issue": "hallucination|misclassification|coverage_gap", "detail": "..."}}
]}}

Return ONLY valid JSON. No markdown fences.
"""


def audit_content(state: AgentState) -> dict:
    """Audit question_bank against knowledge_map for quality."""
    llm = get_llm()
    knowledge_map = state.get("knowledge_map", [])
    question_bank = state.get("question_bank", [])
    audit_flags: list[AuditFlag] = []

    chunk_lookup = {c["chunk_id"]: c for c in knowledge_map}

    # Group questions by chunk
    by_chunk: dict[str, list] = {}
    for q in question_bank:
        by_chunk.setdefault(q["chunk_id"], []).append(q)

    for chunk_id, questions in by_chunk.items():
        chunk = chunk_lookup.get(chunk_id)
        if not chunk:
            continue

        questions_text = json.dumps(questions, indent=2)
        user_msg = (
            f"Chunk topic: {chunk['topic']}\n"
            f"Chunk content: {chunk['content']}\n\n"
            f"Questions:\n{questions_text}"
        )

        response = llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ])

        try:
            result = json.loads(response.content.strip())
        except json.JSONDecodeError:
            audit_flags.append(AuditFlag(
                chunk_id=chunk_id,
                issue="audit_error",
                detail="Auditor returned invalid JSON",
            ))
            continue

        for issue in result.get("issues", []):
            audit_flags.append(AuditFlag(
                chunk_id=chunk_id,
                issue=issue.get("issue", "unknown"),
                detail=issue.get("detail", ""),
            ))

    review_status = "approved" if not audit_flags else "needs_review"
    return {"audit_flags": audit_flags, "review_status": review_status}
