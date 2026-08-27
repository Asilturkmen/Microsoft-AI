from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rag.chunker import Chunk
from rag.database import KnowledgeDatabase
from rag.pipeline import RAGPipeline, UNKNOWN_ANSWER


class FakeEmbeddingModel:
    model_alias = "fake-model"

    def load(self) -> None:
        pass

    def close(self) -> None:
        pass

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0]


class RecordingChatModel:
    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []
        self.loaded = False
        self.closed = False

    def load(self) -> None:
        self.loaded = True

    def complete_messages(self, messages: list[dict[str, str]]) -> str:
        self.messages = messages
        return "Normalizasyon yinelenen verileri azaltır."

    def close(self) -> None:
        self.closed = True


class PipelineTests(unittest.TestCase):
    def test_retrieved_context_question_and_source_reach_chat_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = KnowledgeDatabase(Path(tmp) / "knowledge.db")
            database.replace_chunks(
                [Chunk("databases.md", 1, "Normalization reduces duplicated data.")],
                [[1.0, 0.0]],
                embedding_model_alias="fake-model",
            )
            chat = RecordingChatModel()
            pipeline = RAGPipeline(database, FakeEmbeddingModel(), chat)
            result = pipeline.answer_query("Veriler neden normalize edilir?")
            pipeline.close()

        self.assertEqual(result.sources, ["databases.md"])
        self.assertIn("yalnızca belgelere dayanan", chat.messages[0]["content"])
        self.assertIn("databases.md", chat.messages[1]["content"])
        self.assertIn("Normalization reduces duplicated data", chat.messages[1]["content"])
        self.assertIn("Veriler neden normalize edilir?", chat.messages[1]["content"])
        self.assertTrue(chat.loaded)
        self.assertTrue(chat.closed)

    def test_empty_question_is_rejected_before_model_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            chat = RecordingChatModel()
            pipeline = RAGPipeline(
                KnowledgeDatabase(Path(tmp) / "knowledge.db"), FakeEmbeddingModel(), chat
            )
            with self.assertRaisesRegex(ValueError, "boş"):
                pipeline.answer_query("  ")
        self.assertFalse(chat.loaded)

    def test_low_relevance_uses_deterministic_fallback_without_chat(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = KnowledgeDatabase(Path(tmp) / "knowledge.db")
            database.replace_chunks(
                [Chunk("databases.md", 0, "Database content")],
                [[0.0, 1.0]],
                embedding_model_alias="fake-model",
            )
            chat = RecordingChatModel()
            pipeline = RAGPipeline(database, FakeEmbeddingModel(), chat)
            result = pipeline.answer_query("ilgisiz soru")
            pipeline.close()

        self.assertEqual(result.answer, UNKNOWN_ANSWER)
        self.assertEqual(result.sources, [])
        self.assertTrue(result.used_fallback)
        self.assertEqual(chat.messages, [])


if __name__ == "__main__":
    unittest.main()
