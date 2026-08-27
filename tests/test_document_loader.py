from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

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
            (root / "ignored.docx").write_bytes(b"not a real DOCX")

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
            path = Path(tmp) / "notes.csv"
            path.write_bytes(b"content")
            with self.assertRaisesRegex(UnsupportedDocumentError, "Desteklenmeyen"):
                load_document(path)

    def test_pdf_text_is_extracted_with_source_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ders-notu.pdf"
            path.write_bytes(b"%PDF-test")
            page_one = MagicMock()
            page_one.extract_text.return_value = "Birinci sayfa"
            page_two = MagicMock()
            page_two.extract_text.return_value = "İkinci sayfa"
            reader = MagicMock(is_encrypted=False, pages=[page_one, page_two])

            with patch("rag.document_loader.PdfReader", return_value=reader):
                document = load_document(path)

        self.assertEqual(document.source, "ders-notu.pdf")
        self.assertEqual(document.content, "Birinci sayfa\n\nİkinci sayfa")

    def test_scanned_pdf_without_text_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tarama.pdf"
            path.write_bytes(b"%PDF-test")
            page = MagicMock()
            page.extract_text.return_value = ""
            reader = MagicMock(is_encrypted=False, pages=[page])

            with patch("rag.document_loader.PdfReader", return_value=reader):
                with self.assertRaisesRegex(UnsupportedDocumentError, "OCR"):
                    load_document(path)

    def test_missing_directory_has_clear_error(self) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "Knowledge klasörü"):
            load_documents(Path("definitely-missing-directory"))


if __name__ == "__main__":
    unittest.main()
