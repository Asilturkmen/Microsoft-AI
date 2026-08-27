#!/usr/bin/env python3
"""Yerel SQLite knowledge indeksini Foundry embeddingleriyle yeniden kur."""

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
    print("Yerel knowledge indeksi yeniden oluşturuluyor...", flush=True)
    with FoundryEmbeddingModel() as model:
        result = ingest_documents(KNOWLEDGE_DIR, database, model)
    print(f"Yüklenen belge: {result.document_count}")
    print(f"Üretilen parça: {result.chunk_count}")
    print(f"Embedding oluşturulan parça: {result.chunk_count}")
    print(f"Embedding boyutu: {result.embedding_dimension}")
    print(f"SQLite'a kaydedilen satır: {result.stored_count}")
    print(f"Veritabanı: {DATABASE_PATH}")
    print("Belge indeksleme başarıyla tamamlandı.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
