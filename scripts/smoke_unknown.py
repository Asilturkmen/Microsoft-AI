#!/usr/bin/env python3
"""Verify deterministic unknown-answer behavior with real retrieval."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.pipeline import RAGPipeline, UNKNOWN_ANSWER  # noqa: E402


QUESTIONS = [
    "Who won the 2026 FIFA World Cup?",
    "What ingredients are needed for tiramisu?",
    "How does photosynthesis work in plants?",
]


def main() -> int:
    with RAGPipeline() as pipeline:
        for question in QUESTIONS:
            result = pipeline.answer_query(question)
            top_score = result.retrieved_chunks[0].score
            print(f"Question: {question}")
            print(f"Answer: {result.answer}")
            print(f"Top score: {top_score:.6f}")
            print(f"Fallback: {result.used_fallback}")
            if result.answer != UNKNOWN_ANSWER or not result.used_fallback:
                raise RuntimeError(f"Unknown-answer check failed for: {question}")
    print("All unknown-answer checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
