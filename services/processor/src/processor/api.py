"""FastAPI application — endpoints for the course processor pipeline."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from processor.config import settings
from processor.graph import compile_graph

app = FastAPI(
    title="Course Processor",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {"status": "ok", "mock_llm": settings.mock_llm}


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
        graph = compile_graph()
        result = graph.invoke({"source_path": tmp_path})
    finally:
        os.unlink(tmp_path)

    return JSONResponse(content={
        "chunks": result.get("knowledge_map", []),
        "questions": result.get("question_bank", []),
        "audit_flags": result.get("audit_flags", []),
        "review_status": result.get("review_status"),
    })
