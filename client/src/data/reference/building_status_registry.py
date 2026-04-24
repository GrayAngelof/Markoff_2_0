# client/src/data/reference/building_status_registry.py
"""
Реестр статусов зданий.

Хранит read-only справочник статусов зданий.
Загружается один раз при старте приложения.
"""

# ===== ИМПОРТЫ =====
from typing import Callable, List

from src.data.reference.base import BaseRegistry
from src.models import BuildingStatusDTO
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class BuildingStatusRegistry(BaseRegistry[BuildingStatusDTO]):
    """Реестр статусов зданий (read-only)."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, loader: Callable[[], List[BuildingStatusDTO]]) -> None:
        """
        Args:
            loader: Функция, загружающая список статусов зданий из API
        """
        log.system("BuildingStatusRegistry инициализация")
        super().__init__(loader)
        log.system("BuildingStatusRegistry инициализирован")

    # ---- ЗАЩИЩЁННЫЕ МЕТОДЫ (ПЕРЕОПРЕДЕЛЕНИЕ) ----
    def _log_result(self, count: int) -> None:
        """Логирует результат загрузки статусов зданий."""
        log.success(f"Статусы зданий: {count} записей")