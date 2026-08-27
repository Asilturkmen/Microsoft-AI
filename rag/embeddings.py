"""Local Foundry embedding model lifecycle and vector validation."""

from __future__ import annotations

import math
from typing import Any, Sequence

from config import EMBEDDING_MODEL_ALIAS
from rag.foundry_runtime import get_foundry_manager


def validate_embedding(vector: Sequence[float], expected_dimension: int | None = None) -> list[float]:
    """Return a finite float vector or raise a descriptive error."""
    if not vector:
        raise ValueError("Embedding vector is empty.")
    result = [float(value) for value in vector]
    if not all(math.isfinite(value) for value in result):
        raise ValueError("Embedding vector contains NaN or infinite values.")
    if expected_dimension is not None and len(result) != expected_dimension:
        raise ValueError(
            f"Embedding dimension mismatch: expected {expected_dimension}, got {len(result)}."
        )
    return result


class FoundryEmbeddingModel:
    """Generate document and query embeddings with one local model alias."""

    def __init__(self, model_alias: str = EMBEDDING_MODEL_ALIAS) -> None:
        self.model_alias = model_alias
        self._model: Any | None = None
        self._client: Any | None = None
        self.dimension: int | None = None

    def load(self) -> None:
        if self._client is not None:
            return
        model = get_foundry_manager().catalog.get_model(self.model_alias)
        if model is None:
            raise RuntimeError(
                f"Foundry Local catalog does not contain embedding alias: {self.model_alias}"
            )
        model.download()
        model.load()
        self._model = model
        self._client = model.get_embedding_client()

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed a non-empty batch and enforce dimension consistency."""
        if not texts:
            return []
        if any(not text.strip() for text in texts):
            raise ValueError("Embedding input cannot be empty.")
        self.load()
        response = self._client.generate_embeddings(list(texts))
        if len(response.data) != len(texts):
            raise RuntimeError(
                f"Embedding count mismatch: requested {len(texts)}, received {len(response.data)}."
            )
        vectors: list[list[float]] = []
        for item in response.data:
            vector = validate_embedding(item.embedding, self.dimension)
            if self.dimension is None:
                self.dimension = len(vector)
            vectors.append(vector)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        """Embed a query with the exact same model used for documents."""
        return self.embed_texts([text])[0]

    def close(self) -> None:
        if self._model is not None:
            self._model.unload()
        self._model = None
        self._client = None

    def __enter__(self) -> "FoundryEmbeddingModel":
        self.load()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
