"""Parça metni, kaynak bilgisi ve embeddingler için SQLite kalıcılığı."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from rag.chunker import Chunk
from rag.embeddings import validate_embedding


@dataclass(frozen=True, slots=True)
class StoredChunk:
    id: int
    source: str
    chunk_index: int
    content: str
    embedding: list[float]


@dataclass(frozen=True, slots=True)
class StoredDocument:
    source: str
    chunk_count: int


class KnowledgeDatabase:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY,
                    source TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
                    content TEXT NOT NULL CHECK (length(trim(content)) > 0),
                    embedding TEXT NOT NULL,
                    UNIQUE (source, chunk_index)
                );

                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def replace_chunks(
        self,
        chunks: Sequence[Chunk],
        embeddings: Sequence[Sequence[float]],
        *,
        embedding_model_alias: str,
    ) -> None:
        """Duplicate oluşturmadan knowledge indeksini atomik olarak yeniden kur."""
        if len(chunks) != len(embeddings):
            raise ValueError("Parça ve embedding sayıları eşleşmelidir.")
        if not chunks:
            raise ValueError("Parça olmadan indeks oluşturulamaz.")

        dimension: int | None = None
        rows: list[tuple[str, int, str, str]] = []
        for chunk, raw_vector in zip(chunks, embeddings, strict=True):
            vector = validate_embedding(raw_vector, dimension)
            if dimension is None:
                dimension = len(vector)
            rows.append(
                (
                    chunk.source,
                    chunk.chunk_index,
                    chunk.content,
                    json.dumps(vector, separators=(",", ":")),
                )
            )

        self.initialize()
        with self.connect() as connection:
            connection.execute("DELETE FROM chunks")
            connection.execute("DELETE FROM metadata")
            connection.executemany(
                """
                INSERT INTO chunks (source, chunk_index, content, embedding)
                VALUES (?, ?, ?, ?)
                """,
                rows,
            )
            connection.executemany(
                "INSERT INTO metadata (key, value) VALUES (?, ?)",
                [
                    ("embedding_model_alias", embedding_model_alias),
                    ("embedding_dimension", str(dimension)),
                    ("chunk_count", str(len(rows))),
                ],
            )

    def count_chunks(self) -> int:
        self.initialize()
        with self.connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM chunks").fetchone()
        return int(row["count"])

    def get_metadata(self) -> dict[str, str]:
        self.initialize()
        with self.connect() as connection:
            rows = connection.execute("SELECT key, value FROM metadata ORDER BY key").fetchall()
        return {str(row["key"]): str(row["value"]) for row in rows}

    def get_chunks(self) -> list[StoredChunk]:
        self.initialize()
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, source, chunk_index, content, embedding
                FROM chunks
                ORDER BY source, chunk_index
                """
            ).fetchall()
        chunks: list[StoredChunk] = []
        expected_dimension: int | None = None
        for row in rows:
            vector = validate_embedding(json.loads(row["embedding"]), expected_dimension)
            if expected_dimension is None:
                expected_dimension = len(vector)
            chunks.append(
                StoredChunk(
                    id=int(row["id"]),
                    source=str(row["source"]),
                    chunk_index=int(row["chunk_index"]),
                    content=str(row["content"]),
                    embedding=vector,
                )
            )
        return chunks

    def get_documents(self) -> list[StoredDocument]:
        """İndekslenmiş belgeleri gerçek parça sayılarıyla döndür."""
        self.initialize()
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT source, COUNT(*) AS chunk_count
                FROM chunks
                GROUP BY source
                ORDER BY source COLLATE NOCASE
                """
            ).fetchall()
        return [
            StoredDocument(source=str(row["source"]), chunk_count=int(row["chunk_count"]))
            for row in rows
        ]

    def clear(self) -> None:
        """Son belge silindiğinde indeksi atomik olarak boşalt."""
        self.initialize()
        with self.connect() as connection:
            connection.execute("DELETE FROM chunks")
            connection.execute("DELETE FROM metadata")
