#!/usr/bin/env python3
"""Run answerable questions through the real local RAG pipeline."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.pipeline import RAGPipeline  # noqa: E402


QUESTIONS = [
    "What is database normalization and why is it used?",
    "How are TCP and UDP different?",
    "What does polymorphism allow a program to do?",
]


def main() -> int:
    print("Loading local embedding and chat models...", flush=True)
    with RAGPipeline() as pipeline:
        print("Local RAG pipeline ready.", flush=True)
        for question in QUESTIONS:
            result = pipeline.answer_query(question)
            print(f"\nQuestion: {question}")
            print(f"Answer: {result.answer}")
            print(f"Sources: {', '.join(result.sources)}")
            print(
                "Scores: "
                + ", ".join(f"{chunk.score:.4f}" for chunk in result.retrieved_chunks)
            )
    print("Local models unloaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
