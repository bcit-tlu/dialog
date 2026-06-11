"""Node 0 — Document Parser: PDF/text → raw_text."""

from __future__ import annotations

from processor.state import AgentState


def parse_document(state: AgentState) -> dict:
    """Extract text from the source file and store it in raw_text."""
    source = state.get("source_path", "")

    if source.lower().endswith(".pdf"):
        text = _extract_pdf(source)
    else:
        with open(source, "r", encoding="utf-8") as f:
            text = f.read()

    return {"raw_text": text}


def _extract_pdf(path: str) -> str:
    import fitz  # PyMuPDF

    doc = fitz.open(path)
    pages: list[str] = []
    for page in doc:
        pages.append(page.get_text("text"))
    doc.close()
    return "\n\n".join(pages)
