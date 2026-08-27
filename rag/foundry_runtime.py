"""Shared initialization for the in-process Foundry Local SDK runtime."""

from __future__ import annotations

from foundry_local_sdk import Configuration, FoundryLocalManager

from config import FOUNDRY_APP_NAME


def get_foundry_manager() -> FoundryLocalManager:
    """Return the singleton manager, initializing it once per process."""
    manager = FoundryLocalManager.instance
    if manager is None:
        FoundryLocalManager.initialize(Configuration(app_name=FOUNDRY_APP_NAME))
        manager = FoundryLocalManager.instance
    if manager is None:
        raise RuntimeError("Foundry Local SDK initialization failed.")
    return manager
