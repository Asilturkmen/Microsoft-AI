"""Paragraf ve Markdown başlıklarını gözeten basit belge parçalama."""

from __future__ import annotations

import re
from dataclasses import dataclass

from rag.document_loader import Document


_BLOCK_SEPARATOR = re.compile(r"\n\s*\n+")
_HEADING = re.compile(r"^#{1,6}\s+")


@dataclass(frozen=True, slots=True)
class Chunk:
    source: str
    chunk_index: int
    content: str


def _blocks(text: str) -> list[str]:
    return [block.strip() for block in _BLOCK_SEPARATOR.split(text.strip()) if block.strip()]


def _sections(blocks: list[str]) -> list[list[str]]:
    """Her Markdown başlığını ardından gelen paragraflara bağla."""
    if not any(_HEADING.match(block) for block in blocks):
        return [blocks[index : index + 3] for index in range(0, len(blocks), 3)]

    sections: list[list[str]] = []
    current: list[str] = []
    for block in blocks:
        if _HEADING.match(block) and current:
            sections.append(current)
            current = []
        current.append(block)
    if current:
        sections.append(current)
    return sections


def chunk_document(document: Document, max_chars: int = 1_200) -> list[Chunk]:
    """Anlamlı parçalar üret; kaynak ve kararlı parça indekslerini koru."""
    if max_chars < 100:
        raise ValueError("max_chars en az 100 olmalıdır.")
    blocks = _blocks(document.content)
    if not blocks:
        return []

    contents: list[str] = []
    for section in _sections(blocks):
        current = ""
        for block in section:
            candidate = f"{current}\n\n{block}" if current else block
            if current and len(candidate) > max_chars:
                contents.append(current)
                current = block
            else:
                current = candidate
        if current:
            contents.append(current)

    return [
        Chunk(source=document.source, chunk_index=index, content=content)
        for index, content in enumerate(contents)
    ]


def chunk_documents(documents: list[Document], max_chars: int = 1_200) -> list[Chunk]:
    """Belge başına indeksleri koruyarak bir koleksiyonu parçala."""
    return [
        chunk
        for document in documents
        for chunk in chunk_document(document, max_chars=max_chars)
    ]
