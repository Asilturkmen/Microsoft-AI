#!/usr/bin/env python3
"""Projenin gerçek yerel Foundry sohbet modelini çağırabildiğini kanıtla."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import CHAT_MODEL_ALIAS  # noqa: E402
from rag.llm import FoundryChatModel  # noqa: E402


def main() -> int:
    prompt = "Tek kısa cümleyle Türkçe merhaba de."
    print(f"Yerel model yükleniyor: {CHAT_MODEL_ALIAS}")
    with FoundryChatModel() as model:
        print("Yerel model hazır.")
        print(f"İstem: {prompt}")
        print(f"Yanıt: {model.complete(prompt)}")
    print("Yerel model kaldırıldı.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
