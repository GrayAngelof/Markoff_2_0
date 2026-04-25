# client/src/data/reference/room_status_registry.py
"""
Реестр статусов помещений.

Хранит read-only справочник статусов помещений.
Загружается один раз при старте приложения.
"""

# ===== ИМПОРТЫ =====
from typing import Callable, List

from .base import BaseRegistry
from src.models import RoomStatusDTO
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class RoomStatusRegistry(BaseRegistry[RoomStatusDTO]):
    """Реестр статусов помещений (read-only)."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, loader: Callable[[], List[RoomStatusDTO]]) -> None:
        """
        Args:
            loader: Функция, загружающая список статусов помещений из API
        """
        log.system("RoomStatusRegistry инициализация")
        super().__init__(loader)
        log.system("RoomStatusRegistry инициализирован")

    # ---- ЗАЩИЩЁННЫЕ МЕТОДЫ (ПЕРЕОПРЕДЕЛЕНИЕ) ----
    def _log_result(self, count: int) -> None:
        """Логирует результат загрузки статусов помещений."""
        log.success(f"Статусы помещений: {count} записей")