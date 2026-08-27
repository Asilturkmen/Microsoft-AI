from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rag.database import KnowledgeDatabase
from rag.ingestion import ingest_documents
from web_api.service import RAGWebService


class FakeEmbeddingModel:
    model_alias = "test-model"

    def embed_texts(self, texts):
        return [[float(len(text)), 1.0] for text in texts]


class FakePipeline:
    def __init__(self) -> None:
        self.embedding_model = FakeEmbeddingModel()
        self.is_loaded = False

    def close(self) -> None:
        pass


class WebServiceDocumentTests(unittest.TestCase):
    def test_reads_document_and_delete_rebuilds_remaining_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            knowledge = root / "knowledge"
            knowledge.mkdir()
            (knowledge / "bir.md").write_text("# Bir\n\nBirinci belge içeriği.", encoding="utf-8")
            (knowledge / "iki.md").write_text("# İki\n\nİkinci belge içeriği.", encoding="utf-8")
            database = KnowledgeDatabase(root / "knowledge.db")
            pipeline = FakePipeline()
            ingest_documents(knowledge, database, pipeline.embedding_model)
            service = RAGWebService(knowledge_dir=knowledge, database=database, pipeline=pipeline)

            detail = service.get_document("bir.md")
            result = service.delete_document("bir.md")

            self.assertIn("Birinci belge", detail["content"])
            self.assertFalse((knowledge / "bir.md").exists())
            self.assertTrue((knowledge / "iki.md").exists())
            self.assertEqual(result["document_count"], 1)
            self.assertEqual([item.source for item in database.get_documents()], ["iki.md"])

    def test_delete_last_document_clears_index_and_rejects_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            knowledge = root / "knowledge"
            knowledge.mkdir()
            (knowledge / "tek.md").write_text("Silinecek bilgi.", encoding="utf-8")
            database = KnowledgeDatabase(root / "knowledge.db")
            pipeline = FakePipeline()
            ingest_documents(knowledge, database, pipeline.embedding_model)
            service = RAGWebService(knowledge_dir=knowledge, database=database, pipeline=pipeline)

            with self.assertRaises(ValueError):
                service.get_document("../tek.md")
            result = service.delete_document("tek.md")

            self.assertEqual(result["document_count"], 0)
            self.assertEqual(database.count_chunks(), 0)
            self.assertEqual(database.get_metadata(), {})


if __name__ == "__main__":
    unittest.main()
