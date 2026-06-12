# Dialog — Diagnostic Interactive Assessment of Learning through Open Grading


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

TBD 


## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_API_KEY` | — | **Required.** API key from [ollama.com/settings/keys](https://ollama.com/settings/keys) |
| `OLLAMA_BASE_URL` | `https://ollama.com` | Ollama Cloud endpoint |
| `OLLAMA_MODEL` | `gemma4:31b-cloud` | Chat model |
| `MOCK_LLM` | `false` | Run pipeline with deterministic mock responses |
