# Dialog

Diagnostic Interactive Assessment of Learning through Open Grading

A proof-of-concept prototype that uses multiple AI agents to conduct conversational knowledge assessments with students.

Built with [LangGraph](https://github.com/langchain-ai/langgraph), [LangChain](https://github.com/langchain-ai/langchain), [FastAPI](https://fastapi.tiangolo.com/), [ChromaDB](https://www.trychroma.com/), and [Ollama Cloud](https://ollama.com/) for LLM inference. Features a Next.js chat frontend with streaming responses.

## Architecture

```
User ──► Frontend (3000) ──► API (8000) ──► Ollama (11434)
                                        └──► ChromaDB (8100)
```

| Service       | Role                                  | Port  |
|---------------|---------------------------------------|-------|
| **ollama**    | LLM inference                         | 11434 |
| **chromadb**  | Vector store (shared by api & ingest) | 8100  |
| **api**       | FastAPI backend (LangGraph agent)     | 8000  |
| **frontend**  | Next.js chat UI                       | 3000  |
| **ingestion** | Doc processing worker (on-demand)     | —     |

## Agent Graph

```
User message
     │
     ▼
 [retrieve]  ←── ChromaDB vector store
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
├── docker-compose.yml
├── .env.example
├── docs/                          # Source documents for ingestion
├── services/
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   ├── run_api.py
│   │   ├── ingest_docs.py
│   │   └── src/dialog/
│   │       ├── api.py             # FastAPI (/health, /ingest, /chat, /chat/stream)
│   │       ├── config.py          # Settings loaded from .env
│   │       ├── graph.py           # LangGraph agent (nodes + routing)
│   │       └── vectorstore.py     # ChromaDB ingestion & retrieval
│   └── frontend/
│       ├── Dockerfile
│       ├── package.json
│       └── src/app/               # Next.js App Router
└── README.md
```

## Getting Started

### 1. Configure environment

```bash
cp .env.example .env
# set OLLAMA_API_KEY — get yours at https://ollama.com/settings/keys
```

### 2. Start all services

```bash
docker compose up --build -d
```

This starts Ollama, ChromaDB, the API, and the frontend.

- **Frontend:** http://localhost:3000
- **API docs:** http://localhost:8000/docs
- **ChromaDB:** http://localhost:8100

### 3. Ingest documents

Place documents in the `docs/` directory, then run the ingestion worker:

```bash
docker compose run ingestion /app/docs/your_document.pdf
```

### 4. Chat

Open http://localhost:3000 and start chatting, or use the API directly:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main topics covered in the document?"}'
```

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/ingest` | Upload and ingest a document (PDF or TXT) |
| `POST` | `/chat` | Send a message to the agent (JSON response) |
| `POST` | `/chat/stream` | Send a message with streaming SSE response |

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

### Chat — streaming

```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarise the document"}'
```

### Ingest a file via API

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@path/to/document.pdf"
```

## Local Development

### API service

```bash
cd services/api
uv sync
cp ../../.env .env
uv run python run_api.py
```

### Frontend

```bash
cd services/frontend
npm install
npm run dev
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_API_KEY` | — | **Required.** API key from [ollama.com/settings/keys](https://ollama.com/settings/keys) |
| `OLLAMA_BASE_URL` | `https://ollama.com` | Ollama Cloud endpoint |
| `OLLAMA_MODEL` | `gemma4:31b-cloud` | Chat model |
| `CHROMA_HOST` | `localhost` | ChromaDB hostname |
| `CHROMA_PORT` | `8000` | ChromaDB port |
| `CHUNK_SIZE` | `1000` | Document chunk size in characters |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `RETRIEVAL_K` | `4` | Number of chunks passed to the LLM per query |
