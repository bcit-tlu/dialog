"""FastAPI application — thin wrapper over CourseProcessorGraph."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from dialog.default_config import DEFAULT_CONFIG
from dialog.graph import CourseProcessorGraph

app = FastAPI(
    title="Course Processor",
    version="0.1.0",
)

# Instantiate the graph once at startup
_graph = CourseProcessorGraph(config=DEFAULT_CONFIG)


@app.get("/health")
async def health():
    return {"status": "ok", "mock_llm": DEFAULT_CONFIG.get("mock_llm", False)}


@app.post("/process")
async def process_document(file: UploadFile = File(...)):
    """Upload a PDF or text file and run the full processing pipeline."""
    suffix = Path(file.filename or "upload.txt").suffix
    if suffix.lower() not in (".pdf", ".txt", ".md"):
        raise HTTPException(400, "Only .pdf, .txt, and .md files are supported.")

    # Persist the upload to a temp file so the parse node can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = _graph.process(tmp_path)
    finally:
        os.unlink(tmp_path)

    return JSONResponse(content={
        "chunks": result.get("knowledge_map", []),
        "questions": result.get("question_bank", []),
        "audit_flags": result.get("audit_flags", []),
        "review_status": result.get("review_status"),
    })
