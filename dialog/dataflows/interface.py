"""Data source abstraction — route parsing by file type."""

from __future__ import annotations

from dialog.agents.utils.agent_states import AgentState


def parse_document(state: AgentState) -> dict:
    """Extract text from the source file and store it in raw_text.

    This is a graph node that dispatches to the correct parser
    based on file extension.
    """
    source = state.get("source_path", "")

    if source.lower().endswith(".pdf"):
        from .pdf_parser import extract_pdf
        text = extract_pdf(source)
    else:
        from .text_parser import extract_text
        text = extract_text(source)

    return {"raw_text": text}
