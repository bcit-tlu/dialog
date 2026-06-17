"""Conditional routing logic for the graph.

Currently a placeholder — the pipeline is linear. Future use:
human-in-the-loop gates, retry logic, conditional branching by
department, etc.
"""

from __future__ import annotations


class ConditionalLogic:
    """Routing decisions for conditional edges in the graph."""

    @staticmethod
    def needs_review(state: dict) -> str:
        """Check if audit produced flags that need human review.

        Returns the next node name: 'end' or 'human_review' (future).
        """
        if state.get("audit_flags"):
            # Future: route to human review node
            return "end"
        return "end"
