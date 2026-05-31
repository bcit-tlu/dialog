from typing import Annotated, List

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from .config import settings
from .vectorstore import get_context


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    context: str
    questions: List[str]


def _llm() -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0.7,
        client_kwargs=settings.client_kwargs,
    )


def retrieve_node(state: AgentState) -> dict:
    query = state["messages"][-1].content
    context = get_context(query=query, k=settings.retrieval_k)
    return {"context": context}


def analyse_node(state: AgentState) -> dict:
    context = state["context"]
    system_content = (
        "You are an expert document analyst. "
        "Analyse the provided context and answer the user's question concisely."
    )
    if context.strip():
        system_content += f"\n\nContext:\n{context}"

    messages = [SystemMessage(content=system_content), *state["messages"]]
    response = _llm().invoke(messages)
    return {"messages": [response]}


def generate_questions_node(state: AgentState) -> dict:
    context = state["context"]
    if not context.strip():
        return {
            "questions": [],
            "messages": [SystemMessage(content="No documents found to generate questions from.")],
        }

    prompt = (
        "Based on the following document excerpt, generate 5 insightful questions "
        "that test understanding of the material.\n\n"
        f"Context:\n{context}\n\n"
        "Return the questions as a numbered list."
    )
    response = _llm().invoke([HumanMessage(content=prompt)])
    lines = [
        line.strip()
        for line in response.content.splitlines()
        if line.strip() and line.strip()[0].isdigit()
    ]
    return {"questions": lines, "messages": [response]}


def _router(state: AgentState) -> str:
    content = state["messages"][-1].content.lower()
    question_keywords = [
        "generate questions",
        "create questions",
        "make questions",
        "questions about",
        "quiz me",
        "test me",
    ]
    if any(k in content for k in question_keywords):
        return "generate_questions"
    return "analyse"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("analyse", analyse_node)
    graph.add_node("generate_questions", generate_questions_node)

    graph.add_edge(START, "retrieve")
    graph.add_conditional_edges(
        "retrieve",
        _router,
        {"analyse": "analyse", "generate_questions": "generate_questions"},
    )
    graph.add_edge("analyse", END)
    graph.add_edge("generate_questions", END)

    return graph.compile()


agent = build_graph()
