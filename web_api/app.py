"""FastAPI endpointleri ve production frontend sunumu."""

from __future__ import annotations

import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from config import DATA_DIR, PROJECT_ROOT
from web_api.service import RAGWebService


MAX_PDF_BYTES = 20 * 1024 * 1024
ALLOWED_PDF_CONTENT_TYPES = {"application/pdf", "application/octet-stream"}


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4_000)

    @field_validator("question")
    @classmethod
    def normalize_question(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Soru boş olamaz.")
        return normalized


def create_app(
    service: RAGWebService | None = None,
    *,
    frontend_dir: Path | None = None,
) -> FastAPI:
    rag_service = service or RAGWebService()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        rag_service.close()

    app = FastAPI(
        title="Yerel RAG Çalışma Asistanı API",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.state.rag_service = rag_service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )

    @app.get("/api/health", response_model=None)
    def health() -> dict[str, object]:
        return rag_service.health()

    @app.get("/api/documents", response_model=None)
    def documents() -> dict[str, object]:
        items = rag_service.list_documents()
        return {"documents": items, "total": len(items)}

    @app.get("/api/documents/{filename}", response_model=None)
    def document_content(filename: str) -> dict[str, object]:
        try:
            return rag_service.get_document(filename)
        except (FileNotFoundError, ValueError) as error:
            raise HTTPException(status_code=404, detail="Belge bulunamadı.") from error

    @app.delete("/api/documents/{filename}", response_model=None)
    def delete_document(filename: str) -> dict[str, object]:
        try:
            result = rag_service.delete_document(filename)
        except (FileNotFoundError, ValueError) as error:
            raise HTTPException(status_code=404, detail="Belge bulunamadı.") from error
        except RuntimeError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Belge silinemedi: {error}") from error
        return {"deleted": result}

    @app.post("/api/chat", response_model=None)
    def chat(payload: ChatRequest) -> dict[str, object]:
        try:
            result = rag_service.answer(payload.question)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail=f"Yerel RAG sorgusu tamamlanamadı: {error}",
            ) from error

        sources = [
            {
                "filename": chunk.source,
                "chunk_index": chunk.chunk_index,
                "score": round(chunk.score, 6),
            }
            for chunk in result.retrieved_chunks
            if chunk.source in result.sources
        ]
        return {
            "answer": result.answer,
            "sources": sources,
            "used_fallback": result.used_fallback,
        }

    @app.post(
        "/api/documents",
        status_code=status.HTTP_202_ACCEPTED,
        response_model=None,
    )
    async def upload_document(
        background_tasks: BackgroundTasks,
        file: Annotated[UploadFile, File(description="Metin katmanlı PDF belgesi")],
    ) -> dict[str, object]:
        original_name = file.filename or ""
        filename = Path(original_name).name
        if not filename or filename != original_name or Path(filename).suffix.lower() != ".pdf":
            raise HTTPException(status_code=415, detail="Yalnızca güvenli adlı PDF dosyaları desteklenir.")
        if file.content_type not in ALLOWED_PDF_CONTENT_TYPES:
            raise HTTPException(status_code=415, detail="Dosyanın içerik türü PDF olmalıdır.")

        try:
            rag_service.reserve_filename(filename)
        except FileExistsError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        staged_path: Path | None = None
        size = 0
        try:
            with tempfile.NamedTemporaryFile(
                prefix="rag-upload-",
                suffix=".tmp",
                dir=DATA_DIR,
                delete=False,
            ) as target:
                staged_path = Path(target.name)
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_PDF_BYTES:
                        raise HTTPException(
                            status_code=413,
                            detail="PDF dosyası 20 MB sınırını aşıyor.",
                        )
                    target.write(chunk)
            if size == 0:
                raise HTTPException(status_code=400, detail="Boş dosya yüklenemez.")
            with staged_path.open("rb") as uploaded:
                if uploaded.read(5) != b"%PDF-":
                    raise HTTPException(status_code=415, detail="Dosya geçerli bir PDF başlığı içermiyor.")

            job = rag_service.create_upload_job(staged_path, filename)
            staged_path = None
            background_tasks.add_task(rag_service.process_upload, job.id)
            return {"job": job.to_dict()}
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Dosya kaydedilemedi: {error}") from error
        finally:
            await file.close()
            if staged_path is not None:
                staged_path.unlink(missing_ok=True)
                rag_service.release_filename(filename)

    @app.get("/api/documents/jobs/{job_id}", response_model=None)
    def upload_status(job_id: str) -> dict[str, object]:
        try:
            job = rag_service.get_upload_job(job_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="Yükleme işlemi bulunamadı.") from error
        return {"job": job.to_dict()}

    resolved_frontend = frontend_dir or PROJECT_ROOT / "frontend" / "dist"
    if resolved_frontend.is_dir():
        app.mount("/", StaticFiles(directory=resolved_frontend, html=True), name="frontend")
    else:
        @app.get("/", response_model=None)
        def frontend_missing() -> JSONResponse:
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Frontend build bulunamadı. frontend klasöründe npm run build çalıştırın."
                },
            )

    return app
