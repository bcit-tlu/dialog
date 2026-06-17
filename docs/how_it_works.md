# How Dialog Works

A step-by-step explanation of how the Course Processor pipeline transforms raw nursing course material into structured knowledge chunks and assessment questions.

---

## The Big Picture

```
PDF / Text file
      │
      ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Parse     │ ──▶ │    Chunk    │ ──▶ │  Questions   │ ──▶ │    Audit    │
│  (dataflows) │     │   (agent)   │     │   (agent)    │     │   (agent)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │                    │
  raw_text          knowledge_map         question_bank        audit_flags
                                                              review_status
      └────────────────────┴────────────────────┴────────────────────┘
                                    │
                                    ▼
                            Structured JSON output
                       (chunks, questions, audit flags)
```

The system is a **LangGraph pipeline** — a directed graph where each node transforms the state and passes it to the next. There are no loops or branches in the current pipeline; it runs linearly from start to finish.

---

## Step-by-Step

### Step 1: Document Parsing

**What happens:** The uploaded file (PDF, TXT, or Markdown) is converted into plain text.

**Where:** `dialog/dataflows/`

- PDF files are parsed with **PyMuPDF** — each page's text is extracted and joined together.
- Text and Markdown files are read directly.
- The result is stored as `raw_text` in the pipeline state.

No LLM is involved in this step — it's pure file I/O.

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

### Step 3: Question Generation

**What happens:** For each knowledge chunk, the LLM generates **3 assessment questions** at different levels of Bloom's Taxonomy:

| Level | Tests | Example |
|-------|-------|---------|
| **Recall** | Direct factual memory | "What are the three qSOFA criteria?" |
| **Application** | Applying knowledge to a clinical scenario | "A patient presents with altered mental status and low BP — what score would you assign?" |
| **Analysis** | Comparing, evaluating, or breaking down concepts | "Compare qSOFA with full SOFA in terms of clinical utility at triage." |

**Where:** `dialog/agents/questioner/question_generator.py`

- The LLM is called once per chunk.
- Each question includes the question text, a correct answer, and its Bloom's level.
- Results accumulate in `question_bank`.

---

### Step 4: Quality Audit

**What happens:** The LLM cross-references every generated question against its source chunk to catch problems before they reach learners.

**Where:** `dialog/agents/auditor/quality_auditor.py`

It checks for:
- **Hallucinations** — the answer contains information not present in the chunk.
- **Misclassifications** — the Bloom's level label doesn't match what the question actually tests.
- **Coverage gaps** — key facts in the chunk aren't tested by any question.

If all questions pass, `review_status` is set to `"approved"`. If any issues are found, it's set to `"needs_review"` and the specific problems are listed in `audit_flags`.

---

## How the Pieces Fit Together

### The Orchestrator

`CourseProcessorGraph` (in `dialog/graph/processor_graph.py`) is the single entry point. It:

1. Reads configuration (model, API keys, mock mode) from `default_config.py`.
2. Creates an LLM client via the `llm_clients/` factory.
3. Passes the LLM to each agent factory (`create_semantic_chunker(llm)`, etc.) to produce graph nodes.
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
parse  → writes raw_text
chunk  → reads raw_text,      writes knowledge_map
questions → reads knowledge_map, writes question_bank
audit  → reads both,          writes audit_flags + review_status
```

---

## Entry Points

| Method | Command | Description |
|--------|---------|-------------|
| **API** | `python main.py api` | Starts a FastAPI server at `:8000` with `/process` endpoint |
| **CLI** | `python main.py <file>` | Processes a single file and prints results |
| **Docker** | `docker compose up` | Runs the API in a container |
| **Test** | `pytest tests/ -v` | Runs the pipeline with a mock LLM (no tokens) |
