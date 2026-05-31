import json
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import settings


def _load_store() -> list[str]:
    path = Path(settings.document_store_path)
    if path.exists():
        return json.loads(path.read_text())
    return []


def _save_store(chunks: list[str]) -> None:
    Path(settings.document_store_path).write_text(json.dumps(chunks))


def get_context(k: int | None = None) -> str:
    chunks = _load_store()
    if k:
        chunks = chunks[: k]
    return "\n\n".join(chunks)


def ingest_file(file_path: str) -> int:
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        loader = PyPDFLoader(str(path))
    else:
        loader = TextLoader(str(path))

    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(docs)
    texts = [c.page_content for c in chunks]

    existing = _load_store()
    _save_store(existing + texts)
    return len(texts)
