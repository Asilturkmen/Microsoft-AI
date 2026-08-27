#!/usr/bin/env python3
"""Prove that this project can invoke a real local Foundry chat model."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import CHAT_MODEL_ALIAS  # noqa: E402
from rag.llm import FoundryChatModel  # noqa: E402


def main() -> int:
    prompt = "Say hello in one short sentence."
    print(f"Loading local model: {CHAT_MODEL_ALIAS}")
    with FoundryChatModel() as model:
        print("Local model ready.")
        print(f"Prompt: {prompt}")
        print(f"Response: {model.complete(prompt)}")
    print("Local model unloaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
