"""Web API ile çekirdek RAG hattı arasındaki süreç-içi servis katmanı."""

from __future__ import annotations

import shutil
import threading
import time
import uuid
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Literal

from config import DATABASE_PATH, EMBEDDING_MODEL_ALIAS, KNOWLEDGE_DIR
from rag.database import KnowledgeDatabase
from rag.document_loader import SUPPORTED_SUFFIXES
from rag.document_loader import load_document
from rag.ingestion import ingest_documents
from rag.pipeline import AnswerResult, RAGPipeline


UploadStatus = Literal[
    "queued",
    "extracting",
    "processing",
    "embedding",
    "storing",
    "completed",
    "error",
]


@dataclass(frozen=True, slots=True)
class UploadJob:
    id: str
    filename: str
    status: UploadStatus
    message: str
    created_at: float
    document_count: int | None = None
    chunk_count: int | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_STAGE_MESSAGES: dict[UploadStatus, str] = {
    "queued": "Dosya alındı; işlem sırası bekleniyor.",
    "extracting": "PDF metni çıkarılıyor.",
    "processing": "Belgeler parçalara ayrılıyor.",
    "embedding": "Yerel embeddingler oluşturuluyor.",
    "storing": "Knowledge base güncelleniyor.",
    "completed": "Belge knowledge base'e eklendi.",
    "error": "Belge işlenemedi.",
}


class RAGWebService:
    """Model yaşam döngüsünü paylaşır ve chat/ingestion çakışmasını önler."""

    def __init__(
        self,
        *,
        knowledge_dir: Path = KNOWLEDGE_DIR,
        database: KnowledgeDatabase | None = None,
        pipeline: RAGPipeline | None = None,
    ) -> None:
        self.knowledge_dir = Path(knowledge_dir)
        self.database = database or KnowledgeDatabase(DATABASE_PATH)
        self.pipeline = pipeline or RAGPipeline(database=self.database)
        self._operation_lock = threading.RLock()
        self._jobs_lock = threading.Lock()
        self._jobs: dict[str, UploadJob] = {}
        self._reserved_filenames: set[str] = set()

    def health(self) -> dict[str, object]:
        try:
            chunk_count = self.database.count_chunks()
            metadata = self.database.get_metadata()
            index_ready = (
                chunk_count > 0
                and metadata.get("embedding_model_alias") == EMBEDDING_MODEL_ALIAS
            )
        except Exception as error:
            return {
                "status": "error",
                "local": True,
                "runtime": "error",
                "index_ready": False,
                "message": str(error),
            }
        return {
            "status": "ready" if index_ready else "setup_required",
            "local": True,
            "runtime": "ready" if self.pipeline.is_loaded else "idle",
            "index_ready": index_ready,
            "chunk_count": chunk_count,
            "message": (
                "Foundry Local modelleri hazır."
                if self.pipeline.is_loaded
                else "Yerel indeks hazır; modeller ilk sorguda yüklenir."
            ),
        }

    def list_documents(self) -> list[dict[str, object]]:
        indexed = {item.source: item.chunk_count for item in self.database.get_documents()}
        active = {
            job.filename: job.status
            for job in self._job_snapshots()
            if job.status not in {"completed", "error"}
        }
        documents: list[dict[str, object]] = []
        if not self.knowledge_dir.is_dir():
            return documents
        for path in sorted(self.knowledge_dir.iterdir(), key=lambda item: item.name.lower()):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            chunk_count = indexed.get(path.name, 0)
            documents.append(
                {
                    "filename": path.name,
                    "title": path.stem.replace("-", " ").replace("_", " ").strip().title(),
                    "file_type": path.suffix.removeprefix(".").upper(),
                    "status": active.get(path.name, "ready" if chunk_count else "pending"),
                    "chunk_count": chunk_count,
                }
            )
        return documents

    def get_document(self, filename: str) -> dict[str, object]:
        """Güvenli bir knowledge belgesinin çıkarılmış metnini döndür."""
        path = self._resolve_document(filename)
        document = load_document(path)
        indexed = {item.source: item.chunk_count for item in self.database.get_documents()}
        return {
            "filename": path.name,
            "title": path.stem.replace("-", " ").replace("_", " ").strip().title(),
            "file_type": path.suffix.removeprefix(".").upper(),
            "chunk_count": indexed.get(path.name, 0),
            "character_count": len(document.content),
            "content": document.content,
        }

    def delete_document(self, filename: str) -> dict[str, object]:
        """Belgeyi sil ve kalan knowledge koleksiyonunu yeniden indeksle."""
        path = self._resolve_document(filename)
        with self._jobs_lock:
            if filename in self._reserved_filenames:
                raise RuntimeError("Bu belge şu anda işleniyor; işlem tamamlandıktan sonra tekrar deneyin.")

        tombstone = path.with_name(f".{path.name}.{uuid.uuid4().hex}.deleting")
        with self._operation_lock:
            path.replace(tombstone)
            try:
                remaining = [
                    item
                    for item in self.knowledge_dir.iterdir()
                    if item.is_file() and item.suffix.lower() in SUPPORTED_SUFFIXES
                ]
                if remaining:
                    result = ingest_documents(
                        self.knowledge_dir,
                        self.database,
                        self.pipeline.embedding_model,
                    )
                    document_count = result.document_count
                    chunk_count = result.chunk_count
                else:
                    self.database.clear()
                    document_count = 0
                    chunk_count = 0
                tombstone.unlink()
            except Exception:
                if tombstone.exists():
                    tombstone.replace(path)
                # İndeks güncellemesi son adımda hata verdiyse geri konan dosyayla
                # önceki tutarlı durumu yeniden kurmayı en iyi çabayla dene.
                try:
                    ingest_documents(
                        self.knowledge_dir,
                        self.database,
                        self.pipeline.embedding_model,
                    )
                except Exception:
                    pass
                raise
        return {
            "filename": filename,
            "document_count": document_count,
            "chunk_count": chunk_count,
        }

    def answer(self, question: str) -> AnswerResult:
        with self._operation_lock:
            return self.pipeline.answer_query(question)

    def _resolve_document(self, filename: str) -> Path:
        if not filename or Path(filename).name != filename:
            raise ValueError("Geçersiz belge adı.")
        path = self.knowledge_dir / filename
        if path.suffix.lower() not in SUPPORTED_SUFFIXES or not path.is_file():
            raise FileNotFoundError(filename)
        return path

    def reserve_filename(self, filename: str) -> None:
        with self._jobs_lock:
            destination = self.knowledge_dir / filename
            if filename in self._reserved_filenames or destination.exists():
                raise FileExistsError("Bu ada sahip bir belge knowledge base'de zaten var.")
            self._reserved_filenames.add(filename)

    def release_filename(self, filename: str) -> None:
        with self._jobs_lock:
            self._reserved_filenames.discard(filename)

    def create_upload_job(self, staged_path: Path, filename: str) -> UploadJob:
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        destination = self.knowledge_dir / filename
        destination_created = False
        try:
            with staged_path.open("rb") as source, destination.open("xb") as target:
                destination_created = True
                shutil.copyfileobj(source, target)
            staged_path.unlink()
        except Exception:
            if destination_created:
                destination.unlink(missing_ok=True)
            self.release_filename(filename)
            raise
        job = UploadJob(
            id=uuid.uuid4().hex,
            filename=filename,
            status="queued",
            message=_STAGE_MESSAGES["queued"],
            created_at=time.time(),
        )
        with self._jobs_lock:
            self._jobs[job.id] = job
            self._prune_jobs_locked()
        return job

    def process_upload(self, job_id: str) -> None:
        job = self.get_upload_job(job_id)
        path = self.knowledge_dir / job.filename

        def progress(stage: str) -> None:
            typed_stage = stage if stage in _STAGE_MESSAGES else "processing"
            self._update_job(job_id, status=typed_stage, message=_STAGE_MESSAGES[typed_stage])

        try:
            with self._operation_lock:
                result = ingest_documents(
                    self.knowledge_dir,
                    self.database,
                    self.pipeline.embedding_model,
                    progress=progress,
                )
            self._update_job(
                job_id,
                status="completed",
                message=_STAGE_MESSAGES["completed"],
                document_count=result.document_count,
                chunk_count=result.chunk_count,
            )
        except Exception as error:
            path.unlink(missing_ok=True)
            self._update_job(
                job_id,
                status="error",
                message=f"Belge işlenemedi: {error}",
            )
        finally:
            self.release_filename(job.filename)

    def get_upload_job(self, job_id: str) -> UploadJob:
        with self._jobs_lock:
            job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(job_id)
        return job

    def _job_snapshots(self) -> list[UploadJob]:
        with self._jobs_lock:
            return list(self._jobs.values())

    def _update_job(self, job_id: str, **changes: object) -> None:
        with self._jobs_lock:
            current = self._jobs[job_id]
            self._jobs[job_id] = replace(current, **changes)

    def _prune_jobs_locked(self) -> None:
        if len(self._jobs) <= 100:
            return
        completed = sorted(
            (job for job in self._jobs.values() if job.status in {"completed", "error"}),
            key=lambda job: job.created_at,
        )
        for job in completed[: len(self._jobs) - 100]:
            self._jobs.pop(job.id, None)

    def close(self) -> None:
        with self._operation_lock:
            self.pipeline.close()
