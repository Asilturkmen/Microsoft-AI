from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rag.chunker import Chunk
from rag.database import KnowledgeDatabase
from rag.retrieval import SemanticRetriever, cosine_similarity


class FakeEmbeddingModel:
    model_alias = "fake-model"

    def __init__(self, vector: list[float]) -> None:
        self.vector = vector

    def embed_query(self, text: str) -> list[float]:
        return self.vector


class RetrievalTests(unittest.TestCase):
    def test_cosine_similarity_and_zero_vectors(self) -> None:
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [1.0, 0.0]), 1.0)
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)
        self.assertEqual(cosine_similarity([0.0, 0.0], [1.0, 0.0]), 0.0)
        with self.assertRaisesRegex(ValueError, "dimension"):
            cosine_similarity([1.0], [1.0, 2.0])

    def test_ranks_top_chunks_with_scores_and_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = KnowledgeDatabase(Path(tmp) / "knowledge.db")
            database.replace_chunks(
                [
                    Chunk("databases.md", 0, "Normalization"),
                    Chunk("networking.md", 0, "TCP"),
                    Chunk("oop.md", 0, "Classes"),
                ],
                [[1.0, 0.0], [0.7, 0.7], [0.0, 1.0]],
                embedding_model_alias="fake-model",
            )
            results = SemanticRetriever(
                database, FakeEmbeddingModel([1.0, 0.0])
            ).get_top_chunks("database question", top_k=2)

        self.assertEqual([result.source for result in results], ["databases.md", "networking.md"])
        self.assertAlmostEqual(results[0].score, 1.0)
        self.assertGreater(results[0].score, results[1].score)

    def test_detects_embedding_model_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = KnowledgeDatabase(Path(tmp) / "knowledge.db")
            database.replace_chunks(
                [Chunk("a.md", 0, "A")],
                [[1.0]],
                embedding_model_alias="indexed-model",
            )
            with self.assertRaisesRegex(RuntimeError, "model mismatch"):
                SemanticRetriever(
                    database, FakeEmbeddingModel([1.0])
                ).get_top_chunks("question")

    def test_rejects_empty_query_and_invalid_top_k(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            retriever = SemanticRetriever(
                KnowledgeDatabase(Path(tmp) / "knowledge.db"), FakeEmbeddingModel([1.0])
            )
            with self.assertRaisesRegex(ValueError, "empty"):
                retriever.get_top_chunks(" ")
            with self.assertRaisesRegex(ValueError, "top_k"):
                retriever.get_top_chunks("question", top_k=0)


if __name__ == "__main__":
    unittest.main()
