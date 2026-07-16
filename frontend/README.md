# Dialog Frontend

Vite + React + TypeScript + Tailwind CSS UI for the Dialog course processor.

## Prerequisites

- Node.js 20+
- The backend API running on `http://localhost:8000` (see the repo root
  `README` / `docker compose up`)

## Development

```bash
npm install
npm run dev
```

The app runs at http://localhost:5173. API calls to `/api/*` are proxied
to the backend at `http://localhost:8000` (see `vite.config.ts`), so no
CORS configuration is needed in development.

## Build

```bash
npm run build      # type-check + production build into dist/
npm run preview    # preview the production build locally
```

## Structure

```text
src/
├── App.tsx              # routes: / (upload), /jobs/:id
├── main.tsx            # entry point (router + toaster)
├── types.ts            # types mirroring the API schemas
├── api/client.ts       # typed fetch/XHR wrappers (createJob, getJob, getResults)
├── components/ui/      # shadcn-style primitives (button, card, textarea)
├── lib/utils.ts        # cn() + formatBytes()
└── pages/
    ├── UploadPage.tsx  # drag-drop upload + learning objectives
    └── JobPage.tsx     # placeholder (built out in Step 7)
```

## Routes

- `/` — upload a module (drag-drop or picker), enter learning objectives,
  submit to create a job.
- `/jobs/:id` — job status/results (placeholder until Step 7).
