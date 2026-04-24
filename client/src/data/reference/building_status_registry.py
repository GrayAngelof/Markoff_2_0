# client/src/data/reference/building_status_registry.py
"""
Реестр статусов зданий.

Хранит read-only справочник статусов зданий.
Загружается один раз при старте приложения.
"""

# ===== ИМПОРТЫ =====
from typing import List

from src.data.reference.base import BaseRegistry
from src.models import BuildingStatusDTO
from src.services.api_client import ApiClient
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class BuildingStatusRegistry(BaseRegistry[BuildingStatusDTO]):
    """Реестр статусов зданий (read-only)."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, api_client: ApiClient) -> None:
        log.system("BuildingStatusRegistry инициализация")
        super().__init__(api_client.get_building_statuses)
        log.system("BuildingStatusRegistry инициализирован")

    # ---- ЗАЩИЩЁННЫЕ МЕТОДЫ (ПЕРЕОПРЕДЕЛЕНИЕ) ----
    def _log_result(self, count: int) -> None:
        """Логирует результат загрузки статусов зданий."""
        log.success(f"Статусы зданий: {count} записей")