"""Foundry Local chat model lifecycle and inference."""

from __future__ import annotations

from typing import Any

from config import CHAT_MODEL_ALIAS
from rag.foundry_runtime import get_foundry_manager


class FoundryChatModel:
    """Download, load, use, and unload one Foundry Local chat model."""

    def __init__(self, model_alias: str = CHAT_MODEL_ALIAS) -> None:
        self.model_alias = model_alias
        self._model: Any | None = None
        self._client: Any | None = None

    def load(self) -> None:
        """Initialize Foundry Local and load the configured model once."""
        if self._client is not None:
            return

        manager = get_foundry_manager()

        model = manager.catalog.get_model(self.model_alias)
        if model is None:
            raise RuntimeError(
                f"Foundry Local catalog does not contain model alias: {self.model_alias}"
            )

        model.download()
        model.load()
        self._model = model
        client = model.get_chat_client()
        client.settings.temperature = 0.0
        client.settings.max_tokens = 256
        client.settings.random_seed = 42
        self._client = client

    def complete(self, prompt: str) -> str:
        """Return one local chat completion for a non-empty prompt."""
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        return self.complete_messages([{"role": "user", "content": prompt}])

    def complete_messages(self, messages: list[dict[str, str]]) -> str:
        """Return one local completion for an explicit chat message list."""
        if not messages or any(not message.get("content", "").strip() for message in messages):
            raise ValueError("Chat messages cannot be empty.")
        self.load()
        response = self._client.complete_chat(messages)
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Foundry Local returned an empty chat response.")
        return content.strip()

    def close(self) -> None:
        """Unload the model and release its local runtime resources."""
        if self._model is not None:
            self._model.unload()
        self._model = None
        self._client = None

    def __enter__(self) -> "FoundryChatModel":
        self.load()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
