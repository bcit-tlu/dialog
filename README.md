# Dialog — Medical Knowledge Engineering Pipeline

Transform raw nursing course material into categorized knowledge chunks and
corresponding test questions using a LangGraph pipeline.

See [`implementation_plan.md`](implementation_plan.md) for the full strategy.

## Quick Start

```bash
cp .env.example .env          # fill in your Ollama Cloud key
docker compose up --build
```

The processor API will be available at **http://localhost:8000**.

### Mock Mode (no LLM tokens)

```bash
MOCK_LLM=true docker compose up --build
```

### Endpoints

| Method | Path       | Description                              |
|--------|------------|------------------------------------------|
| GET    | `/health`  | Health check                             |
| POST   | `/process` | Upload a PDF/TXT and run the pipeline    |

### Local Development

```bash
cd services/processor
uv sync
MOCK_LLM=true uv run python run_api.py
```

### Tests

```bash
cd services/processor
uv sync --all-extras
uv run pytest tests/ -v
```

## Project Structure

```
dialog/
├── implementation_plan.md        # Strategy document
├── docker-compose.yml
├── docs/                         # Sample course material
│   └── nursing_sepsis_learning_module.pdf
└── services/
    └── processor/                # LangGraph pipeline service
        ├── Dockerfile
        ├── pyproject.toml
        ├── run_api.py
        ├── src/processor/
        │   ├── config.py         # Settings (env vars)
        │   ├── state.py          # AgentState TypedDict
        │   ├── llm.py            # LLM factory + mock
        │   ├── graph.py          # LangGraph wiring
        │   ├── api.py            # FastAPI endpoints
        │   └── nodes/
        │       ├── parse.py      # Node 0: PDF → text
        │       ├── classify.py   # Node 1: Department classifier
        │       ├── chunk.py      # Node 2: Semantic chunker
        │       ├── questions.py  # Node 3: Question generator
        │       └── audit.py      # Node 4: Quality auditor
        └── tests/
            └── test_graph_mock.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_API_KEY` | — | **Required.** API key from [ollama.com/settings/keys](https://ollama.com/settings/keys) |
| `OLLAMA_BASE_URL` | `https://ollama.com` | Ollama Cloud endpoint |
| `OLLAMA_MODEL` | `gemma4:31b-cloud` | Chat model |
| `MOCK_LLM` | `false` | Run pipeline with deterministic mock responses |
