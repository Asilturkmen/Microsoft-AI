#!/usr/bin/env python3
"""Gerçek retrieval ile deterministik bilinmeyen cevap davranışını doğrula."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.pipeline import RAGPipeline, UNKNOWN_ANSWER  # noqa: E402


QUESTIONS = [
    "2026 FIFA Dünya Kupası'nı kim kazandı?",
    "Tiramisu yapmak için hangi malzemeler gerekir?",
    "Bitkilerde fotosentez nasıl gerçekleşir?",
]


def main() -> int:
    with RAGPipeline() as pipeline:
        for question in QUESTIONS:
            result = pipeline.answer_query(question)
            top_score = result.retrieved_chunks[0].score
            print(f"Soru: {question}")
            print(f"Cevap: {result.answer}")
            print(f"En yüksek skor: {top_score:.6f}")
            print(f"Kontrollü bilinmeyen cevabı: {result.used_fallback}")
            if result.answer != UNKNOWN_ANSWER or not result.used_fallback:
                raise RuntimeError(f"Bilinmeyen cevap kontrolü başarısız: {question}")
    print("Tüm bilinmeyen cevap kontrolleri geçti.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
