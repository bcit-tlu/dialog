# How Dialog Works

A step-by-step explanation of how the Course Processor ingestion pipeline transforms raw course material into structured knowledge chunks.

---

## The Big Picture

```
PDF / Text file
      │
      ▼
┌─────────────┐     ┌─────────────┐
│   Extract    │ ──▶ │    Chunk    │
│  (no LLM)   │     │   (LLM)    │
└─────────────┘     └─────────────┘
      │                    │
  raw_text          knowledge_map
      └────────────────────┘
                │
                ▼
        Structured JSON output
           (knowledge chunks)
```

The system is a **LangGraph pipeline** — a directed graph where each node transforms the state and passes it to the next. The current pipeline is linear: extract → chunk → done.

---

## Step-by-Step

### Step 1: Content Extraction

**What happens:** The uploaded file (PDF, TXT, or Markdown) is converted into plain text.

**Where:** `dialog/agents/extractor/content_extractor.py` → delegates to `dialog/dataflows/`

- PDF files are parsed with **PyMuPDF** — each page's text is extracted and joined together.
- Text and Markdown files are read directly.
- The result is stored as `raw_text` in the pipeline state.

No LLM is involved — this is pure file I/O.

---

### Step 2: Semantic Chunking

**What happens:** The raw text is split into self-contained **Atomic Knowledge Units** — each covering exactly one concept, procedure, or fact.

**Where:** `dialog/agents/chunker/semantic_chunker.py`

- The LLM receives the full text with instructions to identify natural boundaries (headings, procedures, lists).
- It returns a JSON array of `{topic, content}` objects.
- Each chunk gets a unique ID and is stored in `knowledge_map`.

**Example output:**
```json
[
  {"chunk_id": "a1b2c3d4", "topic": "Sepsis Definition", "content": "Sepsis is a life-threatening..."},
  {"chunk_id": "e5f6g7h8", "topic": "qSOFA Criteria", "content": "The quick SOFA score uses..."}
]
```

---

## How the Pieces Fit Together

### The Orchestrator

`CourseProcessorGraph` (in `dialog/graph/processor_graph.py`) is the single entry point. It:

1. Reads configuration (model, API keys, mock mode) from `default_config.py`.
2. Creates an LLM client via the `llm_clients/` factory.
3. Passes the LLM to agent factories to produce graph nodes.
4. Wires the nodes into a LangGraph `StateGraph` via `graph/setup.py`.
5. Compiles the graph and exposes one method: `process(source_path) → result`.

### The Agent Factory Pattern

Each agent is defined as a **factory function**:

```python
def create_semantic_chunker(llm):
    def semantic_chunker_node(state):
        # use llm to chunk state["raw_text"]
        return {"knowledge_map": [...]}
    return semantic_chunker_node
```

The factory captures the LLM in a closure. This means:
- Swapping models is a one-line config change.
- Tests use a mock LLM that returns pre-canned JSON — no tokens spent.
- Each agent is independently testable.

### The State

A single `AgentState` dictionary flows through every node. Each node reads what it needs and writes its output back:

```
extract → writes raw_text
chunk   → reads raw_text, writes knowledge_map
```

---

## Entry Points

| Method | Command | Description |
|--------|---------|-------------|
| **API** | `python main.py api` | Starts a FastAPI server at `:8000` with `/process` endpoint |
| **CLI** | `python main.py <file>` | Processes a single file and prints results |
| **Docker** | `docker compose up` | Runs the API in a container |
| **Test** | `pytest tests/ -v` | Runs the pipeline with a mock LLM (no tokens) |
