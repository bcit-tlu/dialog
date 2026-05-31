# Dialog

A conversational AI agent that analyses documents and generates questions based on the provided material.

Built with [LangGraph](https://github.com/langchain-ai/langgraph), [LangChain](https://github.com/langchain-ai/langchain), [FastAPI](https://fastapi.tiangolo.com/), and [Ollama Cloud](https://ollama.com/) for LLM inference.
Documents are chunked and stored locally as JSON — no embedding model or vector database required.

## Agent Graph

```
User message
     │
     ▼
 [retrieve]  ←── JSON document store
     │
  [router]
     │
     ├── "generate questions / quiz me" ──► [generate_questions] ──► END
     │
     └── (anything else) ─────────────────► [analyse] ─────────────► END
```

## Project Structure

```
dialog/
├── src/
│   └── dialog/
│       ├── __init__.py
│       ├── config.py          # Settings loaded from .env
│       ├── vectorstore.py     # Document ingestion & retrieval (ChromaDB)
│       ├── graph.py           # LangGraph agent (nodes + routing)
│       └── api.py             # FastAPI app (/health, /ingest, /chat)
├── run_api.py                 # Start the API server
├── ingest_docs.py             # CLI: load documents into the vector store
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

## Setup

### 1. Install dependencies

```bash
# with uv (recommended)
uv sync

# or with pip
pip install -e .
```

### 2. Configure environment

```bash
cp .env.example .env
# set OLLAMA_API_KEY — get yours at https://ollama.com/settings/keys
```

### 3. Ingest documents

```bash
python ingest_docs.py path/to/document.pdf path/to/notes.txt
```

### 4. Start the API

```bash
python run_api.py
```

API available at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`.

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/ingest` | Upload and ingest a document (PDF or TXT) |
| `POST` | `/chat` | Send a message to the agent |

### Chat — analyse a document

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main topics covered in the document?"}'
```

### Chat — generate questions

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate questions about the material"}'
```

### Ingest a file via API

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@path/to/document.pdf"
```

## Running with Docker

### 1. Configure `.env`

```bash
cp .env.example .env
# set OLLAMA_API_KEY
```

### 2. Start the app

```bash
docker compose up --build -d
```

Single container — all inference is handled by Ollama Cloud. No local model server required.

### 3. Ingest and chat

```bash
curl -X POST http://localhost:8000/ingest -F "file=@doc.pdf"
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main topics?"}'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_API_KEY` | — | **Required.** API key from [ollama.com/settings/keys](https://ollama.com/settings/keys) |
| `OLLAMA_BASE_URL` | `https://ollama.com` | Ollama Cloud endpoint |
| `OLLAMA_MODEL` | `gemma4:31b-cloud` | Chat model |
| `DOCUMENT_STORE_PATH` | `./document_store.json` | Where ingested document chunks are stored |
| `CHUNK_SIZE` | `1000` | Document chunk size in characters |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `RETRIEVAL_K` | `4` | Number of chunks passed to the LLM per query |
