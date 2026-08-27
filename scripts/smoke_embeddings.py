#!/usr/bin/env python3
"""Generate and inspect real local Foundry embedding vectors."""

from __future__ import annotations

import math
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import EMBEDDING_MODEL_ALIAS  # noqa: E402
from rag.embeddings import FoundryEmbeddingModel  # noqa: E402


def cosine(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    return numerator / math.sqrt(
        sum(value * value for value in left) * sum(value * value for value in right)
    )


def main() -> int:
    texts = [
        "Object-oriented programming uses classes and objects.",
        "Classes are blueprints for creating object instances.",
        "TCP retransmits lost network data.",
    ]
    print(f"Loading local embedding model: {EMBEDDING_MODEL_ALIAS}", flush=True)
    with FoundryEmbeddingModel() as model:
        vectors = model.embed_texts(texts)
        print(f"Vectors: {len(vectors)}", flush=True)
        print(f"Dimension: {len(vectors[0])}", flush=True)
        print(f"Finite: {all(math.isfinite(x) for vector in vectors for x in vector)}", flush=True)
        print(f"Similar cosine: {cosine(vectors[0], vectors[1]):.6f}", flush=True)
        print(f"Different cosine: {cosine(vectors[0], vectors[2]):.6f}", flush=True)
    print("Local embedding model unloaded.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
