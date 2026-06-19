# Implementation Plan: Medical Knowledge Engineering Pipeline
**Project:** Course Processor (Dialog)
**Framework:** LangGraph
**Goal:** Ingest raw course material (any format) and transform it into structured knowledge chunks.
**Architecture Reference:** Modelled after [TradingAgents](https://github.com/TradingAgents) — agent-factory pattern, orchestrator class, clean sub-package separation.

---

## 1. Architectural Overview

The project is structured as a single installable Python package (`dialog/`) at the repo root, with four sub-packages separated by concern. The current pipeline focuses on **ingestion only** (2 agents).

```
dialog/                          # repo root
├── pyproject.toml               # single project file (uv / hatch)
├── main.py                      # quick CLI entry point
├── docker-compose.yml
├── docs/                        # sample course material
├── tests/                       # all tests live here
│
└── dialog/                      # the installable package
    ├── __init__.py
    ├── default_config.py        # config dict + env-var overlay
    │
    ├── agents/                  # agent factories grouped by ROLE
    │   ├── __init__.py          # re-exports create_content_extractor, create_semantic_chunker
    │   ├── schemas.py           # Pydantic structured-output models (ChunkOutput)
    │   ├── extractor/
    │   │   └── content_extractor.py   # create_content_extractor() — no LLM, format detection + text extraction
    │   ├── chunker/
    │   │   └── semantic_chunker.py    # create_semantic_chunker(llm) — LLM-powered semantic splitting
    │   └── utils/
    │       └── agent_states.py        # AgentState TypedDict (KnowledgeChunk)
    │
    ├── graph/                   # graph orchestration — NO agent logic
    │   ├── __init__.py
    │   ├── processor_graph.py   # CourseProcessorGraph orchestrator class
    │   ├── setup.py             # node / edge wiring (extract → chunk → END)
    │   ├── conditional_logic.py # routing (placeholder, future)
    │   └── propagation.py       # initial state creation
    │
    ├── dataflows/               # data-source abstraction (used by extractor agent)
    │   ├── __init__.py
    │   ├── interface.py         # parse_document() dispatcher
    │   ├── pdf_parser.py        # PyMuPDF implementation
    │   └── text_parser.py       # plain text / markdown fallback
    │
    ├── llm_clients/             # LLM provider abstraction
    │   ├── __init__.py
    │   ├── base_client.py       # ABC: get_llm(), validate_model()
    │   ├── factory.py           # create_llm_client(provider, model, ...)
    │   ├── openai_client.py     # Ollama / OpenAI / any compat endpoint
    │   └── mock_client.py       # FakeListChatModel for testing
    │
    └── api.py                   # FastAPI endpoints (thin wrapper over CourseProcessorGraph)
```

### Design Principles (from TradingAgents)
- **Agent factory pattern** — every agent is a `create_X(...) → node_fn` factory. The closure captures dependencies (e.g. LLM), returns partial state. Swap in a mock LLM and the factory still works.
- **Orchestrator class** — `CourseProcessorGraph` is the single public API. It owns LLM creation, config, graph compilation, and the `process()` entry point. Consumers never touch LangGraph directly.
- **Separation of graph wiring from agent logic** — `graph/` only does node registration and edge connections; all prompt/LLM work lives in `agents/`.
- **Structured outputs** — Pydantic schemas in `agents/schemas.py` define what each agent returns, with `render_*()` helpers to convert back to markdown.
- **Not all nodes need an LLM** — the extractor is pure Python; LangGraph nodes are just functions that take state and return partial state.

### State Definition
The `AgentState` (in `agents/utils/agent_states.py`) tracks:
- `source_path`: Path to the uploaded file.
- `raw_text`: The original extracted content (set by extractor).
- `knowledge_map`: A list of `KnowledgeChunk` objects (`chunk_id`, `topic`, `content`) (set by chunker).
- `error`: Optional error message.

---

## 2. The Graph Workflow (Agents)

Each agent is produced by a factory function. The graph wires them in `graph/setup.py`.

### Agent 1: Content Extractor (`create_content_extractor`)
- **Input:** `source_path`
- **Action:** Detect file format and extract raw text. Delegates to `dataflows/` parsers. No LLM needed.
- **Output:** Set `raw_text` in state.
- **Location:** `agents/extractor/content_extractor.py`

### Agent 2: Semantic Chunker (`create_semantic_chunker`)
- **Input:** `raw_text`
- **Action:**
    - Identify natural boundaries (headings, procedures, lists).
    - Split text into "Atomic Knowledge Units."
    - Ensure each chunk is self-contained.
- **Output:** Populate `knowledge_map` with `KnowledgeChunk` objects.
- **Structured Output:** `ChunkOutput` schema in `agents/schemas.py`.
- **Location:** `agents/chunker/semantic_chunker.py`

### Graph Flow
```
START → extract → chunk → END
```

### Future Agents (not yet implemented)
- **Question Generator** — generate assessment questions per chunk.
- **Quality Auditor** — cross-reference questions against source chunks.
- **Department Classifier** — identify nursing specialty from content.

---

## 3. Technical Stack
- **Language:** Python 3.12+
- **Orchestration:** `langgraph`
- **LLM Interface:** `llm_clients/` abstraction layer (Ollama Cloud via OpenAI-compat by default; pluggable for OpenAI, Anthropic, etc.)
- **Parsing:** `dataflows/` abstraction — `PyMuPDF` (fitz) or `Marker` for clean Markdown conversion.
- **Structured Output:** Pydantic models in `agents/schemas.py`
- **API:** FastAPI (thin wrapper in `api.py`)
- **Data Format:** JSONL for intermediate storage (easy to inspect and edit).
- **Package Manager:** `uv`

---

## 4. Execution Phases

### Phase 0: Restructure (The Foundation) ✅
- [x] Flatten to `dialog/` package at repo root.
- [x] Single `pyproject.toml` at repo root.
- [x] Sub-package skeleton: `agents/`, `graph/`, `dataflows/`, `llm_clients/`.
- [x] Agent factories (`create_X(...) → node_fn`).
- [x] LLM abstraction in `llm_clients/` with `BaseLLMClient` ABC + `factory.py`.
- [x] Mock LLM in `llm_clients/mock_client.py`.
- [x] `CourseProcessorGraph` orchestrator in `graph/processor_graph.py`.
- [x] Graph wiring in `graph/setup.py`.
- [x] PDF parsing in `dataflows/pdf_parser.py` behind an interface.
- [x] Pydantic schemas in `agents/schemas.py`.
- [x] Mock test passes against structure.

### Phase 1: Ingestion Pipeline (Current) ✅
- [x] 2-agent pipeline: `extract → chunk → END`.
- [x] Content extractor agent (pure Python, no LLM).
- [x] Semantic chunker agent (LLM-powered).
- [x] Mock LLM tests pass end-to-end.
- [x] `default_config.py` with env-var overlay.
- [x] `api.py` wired to `CourseProcessorGraph.process()`.

### Phase 2: Input Format Flexibility (Next)
- [ ] Support zip file uploads (extract and process multiple files).
- [ ] Detect and handle mixed file types within a zip (PDF, TXT, MD, DOCX).
- [ ] Test with actual emergency nursing sample data.
- [ ] Improve chunker prompts based on real-world output quality.

### Phase 3: Downstream Agents (Future)
- [ ] Add `create_question_generator` — Bloom's Taxonomy questions per chunk.
- [ ] Add `create_quality_auditor` — cross-reference validation.
- [ ] Add structured output schemas wired with `llm.with_structured_output()`.
- [ ] Add "Human-in-the-loop" checkpoints via `graph/conditional_logic.py`.
- [ ] Export utility (CSV/PDF/JSON) for the question bank.
- [ ] Checkpointing support (LangGraph `SqliteSaver`) for crash recovery.
