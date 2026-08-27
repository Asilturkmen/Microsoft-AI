"""Süreç içi Foundry Local SDK çalışma zamanı için ortak başlatma."""

from __future__ import annotations

from foundry_local_sdk import Configuration, FoundryLocalManager

from config import FOUNDRY_APP_NAME


def get_foundry_manager() -> FoundryLocalManager:
    """Tekil yöneticiyi süreç başına bir kez başlatıp döndür."""
    manager = FoundryLocalManager.instance
    if manager is None:
        FoundryLocalManager.initialize(Configuration(app_name=FOUNDRY_APP_NAME))
        manager = FoundryLocalManager.instance
    if manager is None:
        raise RuntimeError("Foundry Local SDK başlatılamadı.")
    return manager
