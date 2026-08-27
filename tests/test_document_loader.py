from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rag.document_loader import (
    UnsupportedDocumentError,
    load_document,
    load_documents,
)


class DocumentLoaderTests(unittest.TestCase):
    def test_loads_supported_files_in_deterministic_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "z.txt").write_text("Text note", encoding="utf-8")
            (root / "A.md").write_text("# Markdown", encoding="utf-8")
            (root / "ignored.pdf").write_bytes(b"not a real PDF")

            documents = load_documents(root)

        self.assertEqual([doc.source for doc in documents], ["A.md", "z.txt"])
        self.assertEqual(documents[0].content, "# Markdown")

    def test_empty_file_is_loaded_safely(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.md"
            path.write_text("", encoding="utf-8")
            document = load_document(path)

        self.assertEqual(document.source, "empty.md")
        self.assertEqual(document.content, "")

    def test_explicit_unsupported_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "notes.pdf"
            path.write_bytes(b"content")
            with self.assertRaisesRegex(UnsupportedDocumentError, "Desteklenmeyen"):
                load_document(path)

    def test_missing_directory_has_clear_error(self) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "Knowledge klasörü"):
            load_documents(Path("definitely-missing-directory"))


if __name__ == "__main__":
    unittest.main()
