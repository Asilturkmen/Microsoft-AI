"""Yerel Foundry embedding modeli yaşam döngüsü ve vektör doğrulaması."""

from __future__ import annotations

import math
from typing import Any, Sequence

from config import EMBEDDING_MODEL_ALIAS
from rag.foundry_runtime import get_foundry_manager


def validate_embedding(vector: Sequence[float], expected_dimension: int | None = None) -> list[float]:
    """Sonlu bir float vektörü döndür veya açıklayıcı hata üret."""
    if not vector:
        raise ValueError("Embedding vektörü boş.")
    result = [float(value) for value in vector]
    if not all(math.isfinite(value) for value in result):
        raise ValueError("Embedding vektörü NaN veya sonsuz değer içeriyor.")
    if expected_dimension is not None and len(result) != expected_dimension:
        raise ValueError(
            f"Embedding boyutu uyuşmuyor: beklenen {expected_dimension}, alınan {len(result)}."
        )
    return result


class FoundryEmbeddingModel:
    """Belge ve sorgu embeddinglerini aynı yerel model alias'ıyla üret."""

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
                f"Foundry Local kataloğunda embedding alias'ı bulunamadı: {self.model_alias}"
            )
        model.download()
        model.load()
        self._model = model
        self._client = model.get_embedding_client()

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Boş olmayan bir grubu embed et ve boyut tutarlılığını zorunlu kıl."""
        if not texts:
            return []
        if any(not text.strip() for text in texts):
            raise ValueError("Embedding girdisi boş olamaz.")
        self.load()
        response = self._client.generate_embeddings(list(texts))
        if len(response.data) != len(texts):
            raise RuntimeError(
                f"Embedding sayısı uyuşmuyor: istenen {len(texts)}, alınan {len(response.data)}."
            )
        vectors: list[list[float]] = []
        for item in response.data:
            vector = validate_embedding(item.embedding, self.dimension)
            if self.dimension is None:
                self.dimension = len(vector)
            vectors.append(vector)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        """Sorguyu belgelerde kullanılan modelin aynısıyla embed et."""
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
