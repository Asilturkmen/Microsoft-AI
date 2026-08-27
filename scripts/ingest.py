#!/usr/bin/env python3
"""Rebuild the local SQLite knowledge index with Foundry embeddings."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import DATABASE_PATH, KNOWLEDGE_DIR  # noqa: E402
from rag.database import KnowledgeDatabase  # noqa: E402
from rag.embeddings import FoundryEmbeddingModel  # noqa: E402
from rag.ingestion import ingest_documents  # noqa: E402


def main() -> int:
    database = KnowledgeDatabase(DATABASE_PATH)
    print("Rebuilding the local knowledge index...", flush=True)
    with FoundryEmbeddingModel() as model:
        result = ingest_documents(KNOWLEDGE_DIR, database, model)
    print(f"Documents loaded: {result.document_count}")
    print(f"Chunks generated: {result.chunk_count}")
    print(f"Chunks embedded: {result.chunk_count}")
    print(f"Embedding dimension: {result.embedding_dimension}")
    print(f"Rows stored in SQLite: {result.stored_count}")
    print(f"Database: {DATABASE_PATH}")
    print("Ingestion completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
