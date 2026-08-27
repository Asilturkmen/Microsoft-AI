#!/usr/bin/env python3
"""SQLite indeksine karşı gerçek Türkçe semantic retrieval soruları çalıştır."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import DATABASE_PATH  # noqa: E402
from rag.database import KnowledgeDatabase  # noqa: E402
from rag.embeddings import FoundryEmbeddingModel  # noqa: E402
from rag.retrieval import SemanticRetriever  # noqa: E402


QUESTIONS = [
    "ACID transaction özellikleri nelerdir?",
    "TCP ile UDP arasındaki farklar nelerdir?",
    "Git dalı ve merge işlemi nedir?",
    "Bir web API hangi HTTP yöntemlerini kullanır?",
]


def main() -> int:
    database = KnowledgeDatabase(DATABASE_PATH)
    with FoundryEmbeddingModel() as model:
        retriever = SemanticRetriever(database, model)
        for question in QUESTIONS:
            results = retriever.get_top_chunks(question)
            print(f"Soru: {question}")
            for result in results:
                print(
                    f"  {result.score:.6f}  {result.source}#{result.chunk_index}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
