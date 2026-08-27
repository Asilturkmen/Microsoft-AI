from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from rag.pipeline import AnswerResult
from rag.retrieval import RetrievedChunk
from web_api.app import create_app
from web_api.service import UploadJob


class FakeWebService:
    def __init__(self) -> None:
        self.closed = False
        self.reserved: set[str] = set()
        self.jobs: dict[str, UploadJob] = {}

    def health(self) -> dict[str, object]:
        return {
            "status": "ready",
            "local": True,
            "runtime": "ready",
            "index_ready": True,
            "chunk_count": 2,
            "message": "Foundry Local modelleri hazır.",
        }

    def list_documents(self) -> list[dict[str, object]]:
        return [
            {
                "filename": "ders.md",
                "title": "Ders",
                "file_type": "MD",
                "status": "ready",
                "chunk_count": 2,
            }
        ]

    def answer(self, question: str) -> AnswerResult:
        return AnswerResult(
            answer=f"Yanıt: {question}",
            sources=["ders.md"],
            retrieved_chunks=[RetrievedChunk(1, "ders.md", 2, "İçerik", 0.8123456)],
        )

    def get_document(self, filename: str) -> dict[str, object]:
        if filename != "ders.md":
            raise FileNotFoundError(filename)
        return {
            "filename": filename,
            "title": "Ders",
            "file_type": "MD",
            "chunk_count": 2,
            "character_count": 6,
            "content": "İçerik",
        }

    def delete_document(self, filename: str) -> dict[str, object]:
        if filename != "ders.md":
            raise FileNotFoundError(filename)
        return {"filename": filename, "document_count": 0, "chunk_count": 0}

    def reserve_filename(self, filename: str) -> None:
        if filename in self.reserved:
            raise FileExistsError("Bu ada sahip bir belge knowledge base'de zaten var.")
        self.reserved.add(filename)

    def release_filename(self, filename: str) -> None:
        self.reserved.discard(filename)

    def create_upload_job(self, staged_path: Path, filename: str) -> UploadJob:
        staged_path.unlink()
        job = UploadJob("job-1", filename, "queued", "Dosya alındı.", time.time())
        self.jobs[job.id] = job
        return job

    def process_upload(self, job_id: str) -> None:
        job = self.jobs[job_id]
        self.jobs[job_id] = UploadJob(
            job.id,
            job.filename,
            "completed",
            "Belge knowledge base'e eklendi.",
            job.created_at,
            1,
            1,
        )
        self.release_filename(job.filename)

    def get_upload_job(self, job_id: str) -> UploadJob:
        if job_id not in self.jobs:
            raise KeyError(job_id)
        return self.jobs[job_id]

    def close(self) -> None:
        self.closed = True


class WebAPITests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FakeWebService()
        self.frontend_tmp = tempfile.TemporaryDirectory()
        self.app = create_app(self.service, frontend_dir=Path(self.frontend_tmp.name) / "missing")

    def tearDown(self) -> None:
        self.frontend_tmp.cleanup()

    def test_health_documents_and_chat_use_real_service_contract(self) -> None:
        with TestClient(self.app) as client:
            health = client.get("/api/health")
            documents = client.get("/api/documents")
            chat = client.post("/api/chat", json={"question": "TCP nedir?"})

        self.assertEqual(health.status_code, 200)
        self.assertTrue(health.json()["local"])
        self.assertEqual(documents.json()["documents"][0]["chunk_count"], 2)
        self.assertEqual(chat.status_code, 200)
        self.assertEqual(chat.json()["sources"][0]["chunk_index"], 2)
        self.assertEqual(chat.json()["sources"][0]["score"], 0.812346)
        self.assertTrue(self.service.closed)

    def test_chat_rejects_whitespace_question(self) -> None:
        with TestClient(self.app) as client:
            response = client.post("/api/chat", json={"question": "   "})

        self.assertEqual(response.status_code, 422)

    def test_document_content_and_delete_use_service_contract(self) -> None:
        with TestClient(self.app) as client:
            content = client.get("/api/documents/ders.md")
            deleted = client.delete("/api/documents/ders.md")
            missing = client.get("/api/documents/missing.md")

        self.assertEqual(content.status_code, 200)
        self.assertEqual(content.json()["content"], "İçerik")
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(deleted.json()["deleted"]["filename"], "ders.md")
        self.assertEqual(missing.status_code, 404)

    def test_upload_rejects_unsupported_or_fake_pdf(self) -> None:
        with TestClient(self.app) as client:
            text_response = client.post(
                "/api/documents",
                files={"file": ("notlar.txt", b"metin", "text/plain")},
            )
            fake_pdf_response = client.post(
                "/api/documents",
                files={"file": ("notlar.pdf", b"PDF degil", "application/pdf")},
            )

        self.assertEqual(text_response.status_code, 415)
        self.assertEqual(fake_pdf_response.status_code, 415)

    def test_valid_pdf_starts_real_background_contract(self) -> None:
        with TestClient(self.app) as client:
            response = client.post(
                "/api/documents",
                files={"file": ("ders.pdf", b"%PDF-1.7\nfixture", "application/pdf")},
            )
            status_response = client.get("/api/documents/jobs/job-1")

        self.assertEqual(response.status_code, 202)
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()["job"]["status"], "completed")

    def test_unknown_upload_job_returns_404(self) -> None:
        with TestClient(self.app) as client:
            response = client.get("/api/documents/jobs/missing")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
