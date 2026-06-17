"""Graph construction — wires nodes and edges, no agent logic here."""

from __future__ import annotations

from typing import Any

from langgraph.graph import StateGraph, END

from dialog.agents.utils.agent_states import AgentState
from dialog.agents import (
    create_semantic_chunker,
    create_question_generator,
    create_quality_auditor,
)
from dialog.dataflows import parse_document


class GraphSetup:
    """Handles the setup and configuration of the processing graph."""

    def __init__(self, llm: Any):
        """Initialize with the LLM instance used by all agent factories."""
        self.llm = llm

    def setup_graph(self) -> StateGraph:
        """Build and return the workflow (uncompiled).

        Pipeline: parse → chunk → questions → audit → END
        """
        workflow = StateGraph(AgentState)

        # Create agent nodes via factories
        chunker_node = create_semantic_chunker(self.llm)
        question_node = create_question_generator(self.llm)
        auditor_node = create_quality_auditor(self.llm)

        # Register nodes
        workflow.add_node("parse", parse_document)
        workflow.add_node("chunk", chunker_node)
        workflow.add_node("questions", question_node)
        workflow.add_node("audit", auditor_node)

        # Wire edges
        workflow.set_entry_point("parse")
        workflow.add_edge("parse", "chunk")
        workflow.add_edge("chunk", "questions")
        workflow.add_edge("questions", "audit")
        workflow.add_edge("audit", END)

        return workflow
