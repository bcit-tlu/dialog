"""State initialization and propagation helpers."""

from __future__ import annotations

from typing import Any, Dict


class Propagator:
    """Handles initial state creation for the graph."""

    def create_initial_state(self, source_path: str) -> Dict[str, Any]:
        """Create the initial state for the processing graph."""
        return {
            "source_path": source_path,
            "raw_text": "",
            "knowledge_map": [],
            "question_bank": [],
            "audit_flags": [],
            "review_status": "pending",
            "error": None,
        }
