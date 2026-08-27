"""Application configuration kept in one dependency-free module."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
DATABASE_PATH = DATA_DIR / "knowledge.db"
TOP_K = 3
UNKNOWN_RELEVANCE_THRESHOLD = 0.50

# These aliases were verified against the local Foundry catalog on 2026-08-27.
CHAT_MODEL_ALIAS = "qwen3.5-2b-text"
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"

FOUNDRY_APP_NAME = "local_rag_assistant"
