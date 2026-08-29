"""Süreç içi Foundry Local SDK çalışma zamanı için ortak başlatma."""

from __future__ import annotations

from typing import TYPE_CHECKING

from config import FOUNDRY_APP_NAME

if TYPE_CHECKING:
    from foundry_local_sdk import FoundryLocalManager


def get_foundry_manager() -> FoundryLocalManager:
    """SDK'yı ilk model kullanımında yükleyip tekil yöneticiyi döndür.

    Foundry SDK, OpenAI istemcisinin geniş tip ağacını içe aktarır. Bu işlemi
    modül yükleme aşamasında yapmak web sunucusunun sağlık endpoint'ini açmasını
    gereksiz yere geciktirir. İçe aktarmayı burada tutarak API'nin model
    yüklemesinden bağımsız biçimde hemen hazır olmasını sağlarız.
    """
    from foundry_local_sdk import Configuration, FoundryLocalManager

    manager = FoundryLocalManager.instance
    if manager is None:
        FoundryLocalManager.initialize(Configuration(app_name=FOUNDRY_APP_NAME))
        manager = FoundryLocalManager.instance
    if manager is None:
        raise RuntimeError("Foundry Local SDK başlatılamadı.")
    return manager
