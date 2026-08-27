"""Kaynak bilgisini koruyarak metin ve PDF bilgi belgelerini yükle."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


SUPPORTED_SUFFIXES = frozenset({".md", ".pdf", ".txt"})


class UnsupportedDocumentError(ValueError):
    """Desteklenmeyen bir dosya türü açıkça istendiğinde oluşturulur."""


@dataclass(frozen=True, slots=True)
class Document:
    source: str
    content: str


def extract_pdf_text(path: Path) -> str:
    """Metin katmanı bulunan bir PDF'nin sayfalarını düz metne dönüştür."""
    try:
        reader = PdfReader(path)
        if reader.is_encrypted and reader.decrypt("") == 0:
            raise UnsupportedDocumentError("Parola korumalı PDF dosyaları desteklenmiyor.")
        pages = [(page.extract_text() or "").replace("\x00", "").strip() for page in reader.pages]
    except UnsupportedDocumentError:
        raise
    except (PdfReadError, OSError, ValueError) as error:
        raise UnsupportedDocumentError(f"PDF metni okunamadı: {path.name}") from error

    content = "\n\n".join(page for page in pages if page).strip()
    if not content:
        raise UnsupportedDocumentError(
            "PDF içinde çıkarılabilir metin bulunamadı. Taranmış görseller için OCR gerekir."
        )
    return content


def load_document(path: Path) -> Document:
    """Bir UTF-8 Markdown, metin veya metin katmanlı PDF belgesini oku."""
    path = Path(path)
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_SUFFIXES))
        raise UnsupportedDocumentError(
            f"Desteklenmeyen belge biçimi: '{path.suffix or '<uzantı yok>'}'. "
            f"Desteklenen biçimler: {supported}."
        )
    if not path.is_file():
        raise FileNotFoundError(f"Belge bulunamadı veya bir dosya değil: {path}")
    if path.suffix.lower() == ".pdf":
        content = extract_pdf_text(path)
    else:
        content = path.read_text(encoding="utf-8")
    return Document(source=path.name, content=content)


def load_documents(directory: Path) -> list[Document]:
    """Klasördeki desteklenen dosyaları ada göre kararlı sırada yükle."""
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"Knowledge klasörü bulunamadı: {directory}")
    paths = sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
        ),
        key=lambda path: path.name.lower(),
    )
    return [load_document(path) for path in paths]
