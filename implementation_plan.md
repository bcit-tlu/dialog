# Implementation Plan: Medical Knowledge Engineering Pipeline
**Project:** Course Processor
**Framework:** LangGraph
**Goal:** Transform raw course material into categorized knowledge chunks and corresponding test questions.

## 1. Architectural Overview
The system will be implemented as a stateful graph where each node represents a specific transformation step.

### State Definition
The `AgentState` object will track:
- `raw_text`: The original extracted content.
- `department`: *(future)* The identified nursing specialty/department.
- `knowledge_map`: A list of processed chunks containing `topic`, `content`, and `chunk_id`.
- `question_bank`: A list of generated questions mapped to `chunk_id`.
- `review_status`: Boolean flags for human-in-the-loop verification.

## 2. The Graph Workflow (Nodes)

### ~~Node 1: Department Classifier (`classify_dept`)~~ *(deferred)*
- **Input:** Raw text.
- **Action:** Analyze the text to determine the specific emergency nursing department (e.g., Triage, Cardiac, Respiratory).
- **Output:** Set `department` in state.
- **Status:** Code exists at `nodes/classify.py` but is not wired into the active graph.

### Node 1: Semantic Chunker (`semantic_chunker`)
- **Input:** Raw text.
- **Action:** 
    - Identify natural boundaries (headings, procedures, lists).
    - Split text into "Atomic Knowledge Units."
    - Ensure each chunk is self-contained.
- **Output:** Populate `knowledge_map`.

### Node 2: Question Generator (`generate_questions`)
- **Input:** `knowledge_map`.
- **Action:** For each chunk, generate a set of questions based on Bloom's Taxonomy (Recall $\rightarrow$ Application $\rightarrow$ Analysis).
- **Output:** Populate `question_bank`.

### Node 3: Quality Auditor (`audit_content`)
- **Input:** `knowledge_map` + `question_bank`.
- **Action:** Cross-reference questions against the chunks to ensure no "hallucinations" occurred and that all key facts are covered.
- **Output:** Flag errors for review or mark as complete.

## 3. Technical Stack
- **Language:** Python 3.12+
- **Orchestration:** `langgraph`
- **LLM Interface:** `langchain_openai` (connecting to Ollama Cloud via OpenAI-compatible API)
- **Parsing:** `PyMuPDF` (fitz) or `Marker` for clean Markdown conversion.
- **Data Format:** JSONL for intermediate storage (easy to inspect and edit).

## 4. Execution Phases

### Phase 1: Infrastructure (The Skeleton)
- [ ] Initialize project directory and virtual environment.
- [ ] Set up basic LangGraph state and node definitions.
- [ ] Implement a "Mock LLM" to test the graph flow without spending tokens.

### Phase 2: Intelligence (The Brain)
- [ ] ~~Implement the `classify_dept` prompt and logic.~~ *(deferred)*
- [ ] Develop the `semantic_chunker` using a combination of regex and LLM-based boundary detection.
- [ ] Create the question generation templates.

### Phase 3: Refinement (The Polish)
- [ ] Add "Human-in-the-loop" checkpoints.
- [ ] Wire in `classify_dept` when department-specific processing is needed.
- [ ] Implement a final export utility (CSV/PDF/JSON) for the question bank.
- [ ] Test with actual emergency nursing sample data.
