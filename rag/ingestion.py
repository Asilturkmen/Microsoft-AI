"""End-to-end local document ingestion orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

from rag.chunker import chunk_documents
from rag.database import KnowledgeDatabase
from rag.document_loader import load_documents


class EmbeddingProvider(Protocol):
    model_alias: str

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]: ...


@dataclass(frozen=True, slots=True)
class IngestionResult:
    document_count: int
    chunk_count: int
    stored_count: int
    embedding_dimension: int


def ingest_documents(
    knowledge_dir: Path,
    database: KnowledgeDatabase,
    embedding_model: EmbeddingProvider,
) -> IngestionResult:
    documents = load_documents(knowledge_dir)
    if not documents:
        raise RuntimeError(f"No supported documents found in {knowledge_dir}")
    chunks = chunk_documents(documents)
    if not chunks:
        raise RuntimeError("Knowledge documents did not produce any non-empty chunks.")
    embeddings = embedding_model.embed_texts([chunk.content for chunk in chunks])
    database.replace_chunks(
        chunks,
        embeddings,
        embedding_model_alias=embedding_model.model_alias,
    )
    stored_count = database.count_chunks()
    if stored_count != len(chunks):
        raise RuntimeError(
            f"SQLite verification failed: expected {len(chunks)} rows, found {stored_count}."
        )
    return IngestionResult(
        document_count=len(documents),
        chunk_count=len(chunks),
        stored_count=stored_count,
        embedding_dimension=len(embeddings[0]),
    )
