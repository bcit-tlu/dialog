import os
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from .graph import agent
from .vectorstore import ingest_file

app = FastAPI(title="Dialog — Document Analysis Agent", version="0.1.0")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    questions: list[str] = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "")[1] or ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        chunks = ingest_file(tmp_path)
        return {"filename": file.filename, "chunks_ingested": chunks}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        os.unlink(tmp_path)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    state = await agent.ainvoke(
        {
            "messages": [HumanMessage(content=request.message)],
            "context": "",
            "questions": [],
        }
    )
    last_message = state["messages"][-1]
    return ChatResponse(
        answer=last_message.content,
        questions=state.get("questions", []),
    )
