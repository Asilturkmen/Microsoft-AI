"""Foundry Local sohbet modeli yaşam döngüsü ve çıkarımı."""

from __future__ import annotations

from typing import Any

from config import CHAT_MODEL_ALIAS
from rag.foundry_runtime import get_foundry_manager


class FoundryChatModel:
    """Bir Foundry Local sohbet modelini indir, yükle, kullan ve kaldır."""

    def __init__(self, model_alias: str = CHAT_MODEL_ALIAS) -> None:
        self.model_alias = model_alias
        self._model: Any | None = None
        self._client: Any | None = None

    def load(self) -> None:
        """Foundry Local'ı başlat ve yapılandırılan modeli bir kez yükle."""
        if self._client is not None:
            return

        manager = get_foundry_manager()

        model = manager.catalog.get_model(self.model_alias)
        if model is None:
            raise RuntimeError(
                f"Foundry Local kataloğunda model alias'ı bulunamadı: {self.model_alias}"
            )

        model.download()
        model.load()
        self._model = model
        client = model.get_chat_client()
        client.settings.temperature = 0.0
        client.settings.max_tokens = 160
        client.settings.random_seed = 42
        self._client = client

    def complete(self, prompt: str) -> str:
        """Boş olmayan bir istem için yerel sohbet yanıtı döndür."""
        if not prompt.strip():
            raise ValueError("İstem boş olamaz.")
        return self.complete_messages([{"role": "user", "content": prompt}])

    def complete_messages(self, messages: list[dict[str, str]]) -> str:
        """Açık bir sohbet mesajı listesi için yerel yanıt döndür."""
        if not messages or any(not message.get("content", "").strip() for message in messages):
            raise ValueError("Sohbet mesajları boş olamaz.")
        self.load()
        response = self._client.complete_chat(messages)
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Foundry Local boş bir sohbet yanıtı döndürdü.")
        return content.strip()

    def close(self) -> None:
        """Modeli kaldır ve yerel çalışma zamanı kaynaklarını serbest bırak."""
        if self._model is not None:
            self._model.unload()
        self._model = None
        self._client = None

    def __enter__(self) -> "FoundryChatModel":
        self.load()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
