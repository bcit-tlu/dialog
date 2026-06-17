# Implementation Plan: Medical Knowledge Engineering Pipeline
**Project:** Course Processor (Dialog)
**Framework:** LangGraph
**Goal:** Transform raw course material into categorized knowledge chunks and corresponding test questions.
**Architecture Reference:** Modelled after [TradingAgents](https://github.com/TradingAgents) — agent-factory pattern, orchestrator class, clean sub-package separation.

---

## 1. Architectural Overview

The project is structured as a single installable Python package (`dialog/`) at the repo root, with four sub-packages separated by concern:

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
    │   ├── __init__.py          # re-exports all create_* functions
    │   ├── schemas.py           # Pydantic structured-output models + render helpers
    │   ├── chunker/
    │   │   └── semantic_chunker.py    # create_semantic_chunker(llm)
    │   ├── questioner/
    │   │   └── question_generator.py  # create_question_generator(llm)
    │   ├── auditor/
    │   │   └── quality_auditor.py     # create_quality_auditor(llm)
    │   ├── classifier/                # (deferred)
    │   │   └── dept_classifier.py     # create_dept_classifier(llm)
    │   └── utils/
    │       ├── agent_states.py        # AgentState + future sub-states
    │       └── agent_utils.py         # shared prompt helpers
    │
    ├── graph/                   # graph orchestration — NO agent logic
    │   ├── __init__.py
    │   ├── processor_graph.py   # CourseProcessorGraph orchestrator class
    │   ├── setup.py             # node / edge wiring
    │   ├── conditional_logic.py # routing (human-in-the-loop gates, future)
    │   └── propagation.py       # initial state creation
    │
    ├── dataflows/               # data-source abstraction
    │   ├── __init__.py
    │   ├── interface.py         # abstract parse interface
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
- **Agent factory pattern** — every agent is a `create_X(llm) → node_fn` factory. The closure captures the LLM, builds a prompt, and returns partial state. Swap in a mock LLM and the factory still works.
- **Orchestrator class** — `CourseProcessorGraph` is the single public API. It owns LLM creation, config, graph compilation, and the `process()` entry point. Consumers never touch LangGraph directly.
- **Separation of graph wiring from agent logic** — `graph/` only does node registration and edge connections; all prompt/LLM work lives in `agents/`.
- **Structured outputs** — Pydantic schemas in `agents/schemas.py` define what each agent returns, with `render_*()` helpers to convert back to markdown.

### State Definition
The `AgentState` (in `agents/utils/agent_states.py`) tracks:
- `source_path`: Path to the uploaded file.
- `raw_text`: The original extracted content.
- `department`: *(future)* The identified nursing specialty/department.
- `knowledge_map`: A list of `KnowledgeChunk` objects (`chunk_id`, `topic`, `content`).
- `question_bank`: A list of `Question` objects mapped to `chunk_id`.
- `audit_flags`: A list of `AuditFlag` objects for issues found.
- `review_status`: Status string for human-in-the-loop verification.
- `error`: Optional error message.

---

## 2. The Graph Workflow (Agents)

Each agent is produced by a factory function: `create_X(llm) → node_function`.
The graph wires them in `graph/setup.py`; routing logic lives in `graph/conditional_logic.py`.

### ~~Agent 0: Department Classifier (`create_dept_classifier`)~~ *(deferred)*
- **Input:** `raw_text`
- **Action:** Analyze text to determine the nursing specialty (Triage, Cardiac, Respiratory, etc.).
- **Output:** Set `department` in state.
- **Location:** `agents/classifier/dept_classifier.py` — exists but not wired into the active graph.

### Agent 1: Semantic Chunker (`create_semantic_chunker`)
- **Input:** `raw_text`
- **Action:**
    - Identify natural boundaries (headings, procedures, lists).
    - Split text into "Atomic Knowledge Units."
    - Ensure each chunk is self-contained.
- **Output:** Populate `knowledge_map` with `KnowledgeChunk` objects.
- **Structured Output:** `ChunkOutput` schema in `agents/schemas.py`.
- **Location:** `agents/chunker/semantic_chunker.py`

### Agent 2: Question Generator (`create_question_generator`)
- **Input:** `knowledge_map`
- **Action:** For each chunk, generate questions based on Bloom's Taxonomy (Recall → Application → Analysis).
- **Output:** Populate `question_bank` with `Question` objects.
- **Structured Output:** `QuestionOutput` schema in `agents/schemas.py`.
- **Location:** `agents/questioner/question_generator.py`

### Agent 3: Quality Auditor (`create_quality_auditor`)
- **Input:** `knowledge_map` + `question_bank`
- **Action:** Cross-reference questions against chunks to detect hallucinations and coverage gaps.
- **Output:** Populate `audit_flags`; set `review_status`.
- **Structured Output:** `AuditResult` schema in `agents/schemas.py`.
- **Location:** `agents/auditor/quality_auditor.py`

### Graph Flow
```
START → parse (dataflows) → chunk → questions → audit → END
                                                   ↑
                                          (future: human gate)
```

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

### Phase 0: Restructure (The Foundation)
- [ ] Flatten `services/processor/src/processor/` → `dialog/` package at repo root.
- [ ] Move `pyproject.toml` to repo root; single installable package.
- [ ] Create sub-package skeleton: `agents/`, `graph/`, `dataflows/`, `llm_clients/`.
- [ ] Move `tests/` to repo root.
- [ ] Migrate existing node functions into agent factories (`create_X(llm) → node_fn`).
- [ ] Extract LLM creation into `llm_clients/` with `BaseLLMClient` ABC + `factory.py`.
- [ ] Move mock LLM into `llm_clients/mock_client.py`.
- [ ] Create `CourseProcessorGraph` orchestrator class in `graph/processor_graph.py`.
- [ ] Move graph wiring into `graph/setup.py`.
- [ ] Move PDF parsing into `dataflows/pdf_parser.py` behind an interface.
- [ ] Add `agents/schemas.py` with Pydantic models for chunk, question, and audit outputs.
- [ ] Verify existing mock test passes against new structure.

### Phase 1: Infrastructure (The Skeleton)
- [x] Initialize project directory and virtual environment.
- [x] Set up basic LangGraph state and node definitions.
- [x] Implement a "Mock LLM" to test the graph flow without spending tokens.
- [ ] Add `default_config.py` with env-var overlay (replace pydantic-settings singleton).
- [ ] Wire `api.py` to use `CourseProcessorGraph.process()`.

### Phase 2: Intelligence (The Brain)
- [ ] ~~Implement the `classify_dept` prompt and logic.~~ *(deferred)*
- [ ] Develop `create_semantic_chunker` using regex + LLM-based boundary detection.
- [ ] Create `create_question_generator` with Bloom's Taxonomy prompt templates.
- [ ] Create `create_quality_auditor` with cross-reference validation logic.
- [ ] Add structured output schemas and wire them with `llm.with_structured_output()`.

### Phase 3: Refinement (The Polish)
- [ ] Add "Human-in-the-loop" checkpoints via `graph/conditional_logic.py`.
- [ ] Wire in `create_dept_classifier` when department-specific processing is needed.
- [ ] Implement a final export utility (CSV/PDF/JSON) for the question bank.
- [ ] Test with actual emergency nursing sample data.
- [ ] Add checkpointing support (LangGraph `SqliteSaver`) for crash recovery.
- [ ] Add reflection / quality feedback loop (inspired by TradingAgents' `Reflector`).
