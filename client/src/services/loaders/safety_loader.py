# client/src/services/loaders/safety_loader.py
"""
SafetyLoader — заглушка для будущей загрузки данных пожарной безопасности.

В будущем будет реализована загрузка:
- Датчиков (дыма, температуры) по помещениям
- Событий пожарной сигнализации по зданиям
"""

# ===== ИМПОРТЫ =====
from typing import Any, List

from src.core import EventBus
from src.services.loaders.base import BaseLoader
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class SafetyLoader(BaseLoader):
    """Заглушка для загрузки данных пожарной безопасности."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus) -> None:
        log.system("SafetyLoader инициализация (заглушка)")
        super().__init__(bus)
        log.system("SafetyLoader инициализирован (заглушка)")

    # ---- ПУБЛИЧНОЕ API ----
    def load_sensors_by_room(self, room_id: int) -> List[Any]:
        """
        Загружает датчики по ID помещения.

        TODO: реализовать загрузку через API
        """
        log.debug(f"SafetyLoader.load_sensors_by_room({room_id}) — заглушка")
        return []

    def load_events_by_building(self, building_id: int) -> List[Any]:
        """
        Загружает события пожарной безопасности по ID здания.

        TODO: реализовать загрузку через API
        """
        log.debug(f"SafetyLoader.load_events_by_building({building_id}) — заглушка")
        return []