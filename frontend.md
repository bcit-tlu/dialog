# Frontend & Async Pipeline — Main Plan

## Goal

Build a React frontend where instructors upload course content (D2L zip, PDF, Word, text) plus their learning objectives, and receive results showing each learning element with a Bloom's taxonomy analysis and source details.

## Why

The current pipeline works end-to-end (parse → chunk) but:
- The `/process` endpoint is synchronous and times out on full modules (~23 LLM calls)
- There is no Bloom's analysis yet
- There is no UI — instructors would need to use curl

## Architecture

```text
React frontend (upload + poll + results)
        ↓
FastAPI api  →  POST /jobs → save file to MinIO → enqueue in Redis → job row in Postgres
        ↓
Worker: dequeue → parse → chunk → classify (Bloom's) → save results to Postgres
        ↓
Frontend polls GET /jobs/{id} → renders learning elements with Bloom's badges
```

## Steps

| # | Step | Description | Size |
|---|------|-------------|------|
| 1 | [DB schema + models](plans/step-01-db-schema.md) | SQLAlchemy models + Alembic migrations for `jobs` and `results` tables | Small |
| 2 | [Async job API](plans/step-02-job-api.md) | `POST /jobs`, `GET /jobs/{id}`, MinIO upload, CORS middleware | Medium |
| 3 | [Worker queue integration](plans/step-03-worker-queue.md) | Redis dequeue loop → run pipeline → save results to DB | Medium |
| 4 | [Bloom's classifier agent](plans/step-04-blooms-classifier.md) | LLM node that tags each chunk with a Bloom's level + rationale | Small |
| 5 | [End-to-end backend test](plans/step-05-backend-e2e-test.md) | Verify the full async flow with curl: upload → poll → results | Small |
| 6 | [React scaffold + upload page](plans/step-06-react-scaffold.md) | Vite + React + TS + Tailwind + shadcn/ui, drag-drop upload page | Medium |
| 7 | [Processing + results pages](plans/step-07-processing-results-pages.md) | Job status polling page, learning element cards with Bloom's badges | Medium |
| 8 | [Frontend Docker integration](plans/step-08-frontend-docker.md) | Frontend Dockerfile (nginx), compose service, API proxy | Small |

## Order & Dependencies

- Steps 1 → 2 → 3 are sequential (each depends on the previous)
- Step 4 is independent — can be done in parallel with 1–3
- Step 5 requires 1–4 complete
- Steps 6 → 7 → 8 are sequential; step 6 can start any time, but 7 needs the API from step 2 to test against

## Definition of Done

An instructor can open the web app, drag in a D2L zip + paste learning objectives, watch processing progress, and browse the resulting learning elements — each showing topic, content, Bloom's level with rationale, and source page — all running via `docker compose up`.