"""LangGraph workflow — wires up all nodes into a linear pipeline."""

from __future__ import annotations

from langgraph.graph import StateGraph, END

from processor.state import AgentState
from processor.nodes import (
    parse_document,
    semantic_chunker,
    generate_questions,
    audit_content,
)


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("parse", parse_document)
    graph.add_node("chunk", semantic_chunker)
    graph.add_node("questions", generate_questions)
    graph.add_node("audit", audit_content)

    graph.set_entry_point("parse")
    graph.add_edge("parse", "chunk")
    graph.add_edge("chunk", "questions")
    graph.add_edge("questions", "audit")
    graph.add_edge("audit", END)

    return graph


def compile_graph():
    return build_graph().compile()
