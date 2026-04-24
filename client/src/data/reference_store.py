# client/src/data/reference_store.py
"""
ReferenceStore — фасад для доступа к справочным данным.

Единая точка входа для всех read-only справочников.
Хранит все реестры и управляет их инициализацией.

Используется только в Projections для маппинга ID → DTO.
Не содержит бизнес-логики, только данные.

Пример:
    store = ReferenceStore(
        building_loader=api_client.get_building_statuses,
        room_loader=api_client.get_room_statuses,
    )
    store.warmup()
    
    status = store.building_statuses.get(1)
    name = status.name if status else None
"""

# ===== ИМПОРТЫ =====
from typing import Callable, List

from src.data.reference.building_status_registry import BuildingStatusRegistry
from src.data.reference.room_status_registry import RoomStatusRegistry
from src.models import BuildingStatusDTO, RoomStatusDTO
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class ReferenceStore:
    """Фасад для доступа к справочным данным."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(
        self,
        building_loader: Callable[[], List[BuildingStatusDTO]],
        room_loader: Callable[[], List[RoomStatusDTO]],
    ) -> None:
        """
        Инициализирует фасад (без загрузки данных).

        Args:
            building_loader: Функция для загрузки статусов зданий
            room_loader: Функция для загрузки статусов помещений
        """
        log.system("ReferenceStore инициализация")

        self._building_statuses = BuildingStatusRegistry(building_loader)
        self._room_statuses = RoomStatusRegistry(room_loader)

        log.system("ReferenceStore инициализирован (данные не загружены)")

    def warmup(self) -> None:
        """Загружает все справочники. Вызывается один раз при старте."""
        log.info("Загрузка справочников ReferenceStore...")

        self._building_statuses.warmup()
        self._room_statuses.warmup()

        log.success("Все справочники загружены")

    def is_ready(self) -> bool:
        """Проверяет, загружены ли все справочники."""
        return self._building_statuses.is_ready() and self._room_statuses.is_ready()

    # ---- ПУБЛИЧНЫЕ АКСЕССОРЫ (READ-ONLY) ----
    @property
    def building_statuses(self) -> BuildingStatusRegistry:
        """Возвращает реестр статусов зданий."""
        return self._building_statuses

    @property
    def room_statuses(self) -> RoomStatusRegistry:
        """Возвращает реестр статусов помещений."""
        return self._room_statuses