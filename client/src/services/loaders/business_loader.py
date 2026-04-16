# client/src/services/loaders/business_loader.py
"""
BusinessLoader — заглушка для будущей загрузки бизнес-данных.

В будущем будет реализована загрузка:
- Контрагентов (юридические лица)
- Ответственных лиц (контакты контрагентов)
"""

# ===== ИМПОРТЫ =====
from typing import Any, List, Optional

from src.core import EventBus
from src.services.loaders.base import BaseLoader
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class BusinessLoader(BaseLoader):
    """Заглушка для загрузки бизнес-данных (контрагенты, ответственные лица)."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus) -> None:
        log.system("BusinessLoader инициализация (заглушка)")
        super().__init__(bus)
        log.system("BusinessLoader инициализирован (заглушка)")

    # ---- ПУБЛИЧНОЕ API ----
    def load_counterparty(self, counterparty_id: int) -> Optional[Any]:
        """
        Загружает контрагента по ID.

        TODO: реализовать загрузку через API
        """
        log.debug(f"BusinessLoader.load_counterparty({counterparty_id}) — заглушка")
        return None

    def load_responsible_persons(self, counterparty_id: int) -> List[Any]:
        """
        Загружает ответственных лиц контрагента.

        TODO: реализовать загрузку через API
        """
        log.debug(f"BusinessLoader.load_responsible_persons({counterparty_id}) — заглушка")
        return []