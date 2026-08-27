from __future__ import annotations

import unittest

from rag.chunker import chunk_document, chunk_documents
from rag.document_loader import Document


class ChunkingTests(unittest.TestCase):
    def test_markdown_headings_produce_multiple_useful_chunks(self) -> None:
        document = Document(
            source="sample.md",
            content=(
                "# Topic\n\nOverview paragraph.\n\n"
                "## First\n\nFirst explanation.\n\n"
                "## Second\n\nSecond explanation."
            ),
        )

        chunks = chunk_document(document)

        self.assertEqual(len(chunks), 3)
        self.assertIn("Overview paragraph", chunks[0].content)
        self.assertIn("First explanation", chunks[1].content)
        self.assertIn("Second explanation", chunks[2].content)

    def test_empty_and_whitespace_input_is_safe(self) -> None:
        self.assertEqual(chunk_document(Document("empty.txt", "  \n")), [])

    def test_source_and_indexes_are_preserved(self) -> None:
        chunks = chunk_document(
            Document("networking.md", "# One\n\nA.\n\n# Two\n\nB.")
        )
        self.assertEqual([chunk.source for chunk in chunks], ["networking.md"] * 2)
        self.assertEqual([chunk.chunk_index for chunk in chunks], [0, 1])

    def test_plain_paragraphs_are_grouped_without_tiny_fragments(self) -> None:
        paragraphs = [f"Paragraph {index}." for index in range(7)]
        chunks = chunk_document(Document("notes.txt", "\n\n".join(paragraphs)))
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0].content.count("Paragraph"), 3)

    def test_collection_keeps_per_document_indexes(self) -> None:
        chunks = chunk_documents(
            [
                Document("a.md", "# A\n\nText"),
                Document("b.md", "# B\n\nText"),
            ]
        )
        self.assertEqual([(c.source, c.chunk_index) for c in chunks], [("a.md", 0), ("b.md", 0)])

    def test_rejects_unreasonably_small_limit(self) -> None:
        with self.assertRaisesRegex(ValueError, "en az 100"):
            chunk_document(Document("a.md", "content"), max_chars=20)


if __name__ == "__main__":
    unittest.main()
