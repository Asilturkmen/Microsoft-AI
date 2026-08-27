from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rag.chunker import Chunk
from rag.database import KnowledgeDatabase


class DatabaseTests(unittest.TestCase):
    def test_replace_persists_chunks_embeddings_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = KnowledgeDatabase(Path(tmp) / "knowledge.db")
            chunks = [Chunk("a.md", 0, "Alpha"), Chunk("b.md", 0, "Beta")]
            database.replace_chunks(
                chunks,
                [[1.0, 0.0], [0.0, 1.0]],
                embedding_model_alias="test-embedding",
            )

            stored = database.get_chunks()
            metadata = database.get_metadata()
            count = database.count_chunks()

        self.assertEqual(count, 2)
        self.assertEqual([item.content for item in stored], ["Alpha", "Beta"])
        self.assertEqual(stored[0].embedding, [1.0, 0.0])
        self.assertEqual(metadata["embedding_model_alias"], "test-embedding")
        self.assertEqual(metadata["embedding_dimension"], "2")

    def test_rebuild_replaces_rows_instead_of_duplicating(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = KnowledgeDatabase(Path(tmp) / "knowledge.db")
            database.replace_chunks(
                [Chunk("old.md", 0, "Old")],
                [[1.0, 0.0]],
                embedding_model_alias="model",
            )
            database.replace_chunks(
                [Chunk("new.md", 0, "New")],
                [[0.0, 1.0]],
                embedding_model_alias="model",
            )
            stored = database.get_chunks()

        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0].source, "new.md")

    def test_rejects_count_and_dimension_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = KnowledgeDatabase(Path(tmp) / "knowledge.db")
            with self.assertRaisesRegex(ValueError, "counts"):
                database.replace_chunks(
                    [Chunk("a.md", 0, "A")],
                    [],
                    embedding_model_alias="model",
                )
            with self.assertRaisesRegex(ValueError, "dimension mismatch"):
                database.replace_chunks(
                    [Chunk("a.md", 0, "A"), Chunk("a.md", 1, "B")],
                    [[1.0], [1.0, 2.0]],
                    embedding_model_alias="model",
                )


if __name__ == "__main__":
    unittest.main()
