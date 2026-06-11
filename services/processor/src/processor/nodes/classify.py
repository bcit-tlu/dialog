"""Node 1 — Department Classifier: Determine the nursing specialty."""

from __future__ import annotations

from processor.llm import get_llm
from processor.state import AgentState

SYSTEM_PROMPT = """\
You are a medical curriculum classifier. Given the text of a nursing course module,
identify the single most appropriate emergency nursing department or specialty.

Respond with ONLY the department name (e.g., "Triage", "Cardiac", "Respiratory",
"Trauma", "Pediatric Emergency", "Sepsis/Infectious Disease").
No explanation, no extra text.
"""


def classify_dept(state: AgentState) -> dict:
    """Classify raw_text into a department."""
    llm = get_llm()
    raw = state.get("raw_text", "")

    # Truncate to first ~3000 chars for classification — enough context
    snippet = raw[:3000]

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": snippet},
    ])

    department = response.content.strip().strip('"').strip("'")
    return {"department": department}
