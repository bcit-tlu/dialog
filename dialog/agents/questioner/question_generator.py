"""Question Generator agent — creates Bloom's Taxonomy questions per chunk."""

from __future__ import annotations

import json
import uuid

from dialog.agents.utils.agent_states import AgentState, Question

SYSTEM_PROMPT = """\
You are a nursing education assessment designer. For the given knowledge chunk,
generate exactly 3 questions at different Bloom's Taxonomy levels:

1. **Recall** — tests direct factual memory.
2. **Application** — requires applying the concept to a clinical scenario.
3. **Analysis** — requires comparing, evaluating, or breaking down the concept.

Return a JSON array of objects with keys:
- "bloom_level": one of "recall", "application", "analysis"
- "question_text": the question
- "answer_text": a concise correct answer

Return ONLY the JSON array. No markdown fences, no explanation.
"""


def create_question_generator(llm):
    """Factory: create a question generator node that captures the given LLM."""

    def question_generator_node(state: AgentState) -> dict:
        """Generate questions for each chunk in knowledge_map."""
        knowledge_map = state.get("knowledge_map", [])
        question_bank: list[Question] = []

        for chunk in knowledge_map:
            user_msg = f"Topic: {chunk['topic']}\n\n{chunk['content']}"

            response = llm.invoke([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ])

            try:
                questions_raw = json.loads(response.content.strip())
            except json.JSONDecodeError:
                continue

            for q in questions_raw:
                question_bank.append(
                    Question(
                        question_id=str(uuid.uuid4())[:8],
                        chunk_id=chunk["chunk_id"],
                        bloom_level=q.get("bloom_level", "recall"),
                        question_text=q.get("question_text", ""),
                        answer_text=q.get("answer_text", ""),
                    )
                )

        return {"question_bank": question_bank}

    return question_generator_node
