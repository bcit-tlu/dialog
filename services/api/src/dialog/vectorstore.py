import hashlib
from pathlib import Path

import chromadb
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import settings

COLLECTION_NAME = "documents"


def _get_client() -> chromadb.ClientAPI:
    return chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)


def _get_collection() -> chromadb.Collection:
    client = _get_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def get_context(query: str, k: int | None = None) -> str:
    collection = _get_collection()
    if collection.count() == 0:
        return ""
    results = collection.query(
        query_texts=[query],
        n_results=k or settings.retrieval_k,
    )
    documents = results.get("documents", [[]])
    return "\n\n".join(documents[0])


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

    ids = [
        hashlib.sha256(f"{file_path}:{i}:{t[:64]}".encode()).hexdigest()[:16]
        for i, t in enumerate(texts)
    ]

    collection = _get_collection()
    batch_size = 5000
    for start in range(0, len(texts), batch_size):
        end = start + batch_size
        collection.add(
            documents=texts[start:end],
            ids=ids[start:end],
        )
    return len(texts)
