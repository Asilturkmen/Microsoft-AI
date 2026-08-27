#!/usr/bin/env python3
"""Bir PDF'yi gerçek API, Foundry modelleri ve geçici SQLite ile uçtan uca doğrula."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.database import KnowledgeDatabase  # noqa: E402
from rag.pipeline import RAGPipeline  # noqa: E402
from web_api.app import create_app  # noqa: E402
from web_api.service import RAGWebService  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="Metin katmanı bulunan test PDF'si")
    parser.add_argument(
        "--question",
        default="Kuzey Yıldızı protokolünün doğrulama kodu nedir?",
        help="Yüklenen PDF'ye sorulacak soru",
    )
    parser.add_argument(
        "--expected-term",
        default="MAVI-47",
        help="Yanıtta bulunması gereken terim",
    )
    args = parser.parse_args()
    pdf_path = args.pdf.resolve()
    if not pdf_path.is_file():
        parser.error(f"PDF bulunamadı: {pdf_path}")

    with tempfile.TemporaryDirectory(prefix="rag-pdf-smoke-") as temporary:
        root = Path(temporary)
        knowledge_dir = root / "knowledge"
        knowledge_dir.mkdir()
        database = KnowledgeDatabase(root / "knowledge.db")
        pipeline = RAGPipeline(database=database)
        service = RAGWebService(
            knowledge_dir=knowledge_dir,
            database=database,
            pipeline=pipeline,
        )
        app = create_app(service, frontend_dir=root / "frontend-yok")

        with TestClient(app) as client, pdf_path.open("rb") as pdf_file:
            upload = client.post(
                "/api/documents",
                files={"file": (pdf_path.name, pdf_file, "application/pdf")},
            )
            upload.raise_for_status()
            job_id = upload.json()["job"]["id"]
            job = client.get(f"/api/documents/jobs/{job_id}")
            job.raise_for_status()
            job_data = job.json()["job"]
            print(f"PDF işleme durumu: {job_data['status']}")
            print(f"İndekslenen parça: {job_data['chunk_count']}")
            if job_data["status"] != "completed":
                raise RuntimeError(job_data["message"])

            response = client.post("/api/chat", json={"question": args.question})
            response.raise_for_status()
            answer = response.json()
            print(f"Soru: {args.question}")
            print(f"Cevap: {answer['answer']}")
            print(f"Kaynaklar: {answer['sources']}")
            if answer["used_fallback"]:
                raise RuntimeError("Yüklenen PDF sorgusu kontrollü bilinmeyen cevabına düştü.")
            if pdf_path.name not in {source["filename"] for source in answer["sources"]}:
                raise RuntimeError("Yüklenen PDF kaynaklar arasında bulunamadı.")
            if args.expected_term.lower() not in answer["answer"].lower():
                raise RuntimeError(
                    f"Beklenen terim yanıtta bulunamadı: {args.expected_term}"
                )

    print("Gerçek PDF upload → ingestion → retrieval → cevap testi PASS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
