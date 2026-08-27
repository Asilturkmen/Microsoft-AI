"""Yerel SQLite indeksi üzerinde embedding tabanlı anlamsal retrieval."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

from config import TOP_K
from rag.database import KnowledgeDatabase


class QueryEmbeddingProvider(Protocol):
    model_alias: str

    def embed_query(self, text: str) -> list[float]: ...


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    id: int
    source: str
    chunk_index: int
    content: str
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Sıfır vektörleri de gözeterek cosine similarity'yi güvenle hesapla."""
    if len(left) != len(right):
        raise ValueError(
            f"Vektör boyutları uyuşmuyor: sol {len(left)}, sağ {len(right)}."
        )
    if not left:
        raise ValueError("Vektörler boş olamaz.")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)


class SemanticRetriever:
    def __init__(
        self,
        database: KnowledgeDatabase,
        embedding_model: QueryEmbeddingProvider,
    ) -> None:
        self.database = database
        self.embedding_model = embedding_model

    def get_top_chunks(self, query: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
        if not query.strip():
            raise ValueError("Sorgu boş olamaz.")
        if top_k < 1:
            raise ValueError("top_k en az 1 olmalıdır.")

        metadata = self.database.get_metadata()
        indexed_alias = metadata.get("embedding_model_alias")
        if indexed_alias != self.embedding_model.model_alias:
            raise RuntimeError(
                "Embedding modeli uyuşmuyor: SQLite indeksi "
                f"'{indexed_alias or '<eksik>'}', sorgular ise "
                f"'{self.embedding_model.model_alias}' kullanıyor. Ingestion'ı yeniden çalıştırın."
            )
        stored_chunks = self.database.get_chunks()
        if not stored_chunks:
            raise RuntimeError("SQLite knowledge indeksi boş. Önce ingestion çalıştırın.")

        query_embedding = self.embedding_model.embed_query(query)
        ranked = sorted(
            (
                RetrievedChunk(
                    id=chunk.id,
                    source=chunk.source,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    score=cosine_similarity(query_embedding, chunk.embedding),
                )
                for chunk in stored_chunks
            ),
            key=lambda item: (-item.score, item.source, item.chunk_index),
        )
        return ranked[: min(top_k, len(ranked))]
