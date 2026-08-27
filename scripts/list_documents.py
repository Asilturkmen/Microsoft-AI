#!/usr/bin/env python3
"""List knowledge documents accepted by the local loader."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.document_loader import load_documents  # noqa: E402


def main() -> int:
    documents = load_documents(PROJECT_ROOT / "knowledge")
    print(f"Loaded {len(documents)} documents.")
    for document in documents:
        empty_note = " (empty)" if not document.content.strip() else ""
        print(f"- {document.source}{empty_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
