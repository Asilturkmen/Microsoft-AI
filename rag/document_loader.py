"""Load plain-text knowledge documents while preserving source metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_SUFFIXES = frozenset({".md", ".txt"})


class UnsupportedDocumentError(ValueError):
    """Raised when a caller explicitly requests an unsupported file type."""


@dataclass(frozen=True, slots=True)
class Document:
    source: str
    content: str


def load_document(path: Path) -> Document:
    """Read one UTF-8 Markdown or text document."""
    path = Path(path)
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_SUFFIXES))
        raise UnsupportedDocumentError(
            f"Unsupported document format '{path.suffix or '<none>'}'. "
            f"Supported formats: {supported}."
        )
    if not path.is_file():
        raise FileNotFoundError(f"Document does not exist or is not a file: {path}")
    return Document(source=path.name, content=path.read_text(encoding="utf-8"))


def load_documents(directory: Path) -> list[Document]:
    """Load supported files from a directory in deterministic filename order."""
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"Knowledge directory does not exist: {directory}")
    paths = sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
        ),
        key=lambda path: path.name.lower(),
    )
    return [load_document(path) for path in paths]
