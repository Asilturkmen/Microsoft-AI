#!/usr/bin/env python3
"""Cevaplanabilir Türkçe soruları gerçek yerel RAG hattında çalıştır."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.pipeline import RAGPipeline  # noqa: E402


QUESTIONS = [
    "ACID transaction özellikleri nelerdir?",
    "TCP ile UDP arasındaki farklar nelerdir?",
    "Unit test ile end-to-end test arasındaki fark nedir?",
]


def main() -> int:
    print("Yerel embedding ve sohbet modelleri yükleniyor...", flush=True)
    with RAGPipeline() as pipeline:
        print("Yerel RAG hattı hazır.", flush=True)
        for question in QUESTIONS:
            result = pipeline.answer_query(question)
            print(f"\nSoru: {question}")
            print(f"Cevap: {result.answer}")
            print(f"Kaynaklar: {', '.join(result.sources)}")
            print(
                "Skorlar: "
                + ", ".join(f"{chunk.score:.4f}" for chunk in result.retrieved_chunks)
            )
    print("Yerel modeller kaldırıldı.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
