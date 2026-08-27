"""Kaynak bilgisini koruyarak düz metin bilgi belgelerini yükle."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_SUFFIXES = frozenset({".md", ".txt"})


class UnsupportedDocumentError(ValueError):
    """Desteklenmeyen bir dosya türü açıkça istendiğinde oluşturulur."""


@dataclass(frozen=True, slots=True)
class Document:
    source: str
    content: str


def load_document(path: Path) -> Document:
    """Bir UTF-8 Markdown veya metin belgesini oku."""
    path = Path(path)
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_SUFFIXES))
        raise UnsupportedDocumentError(
            f"Desteklenmeyen belge biçimi: '{path.suffix or '<uzantı yok>'}'. "
            f"Desteklenen biçimler: {supported}."
        )
    if not path.is_file():
        raise FileNotFoundError(f"Belge bulunamadı veya bir dosya değil: {path}")
    return Document(source=path.name, content=path.read_text(encoding="utf-8"))


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
