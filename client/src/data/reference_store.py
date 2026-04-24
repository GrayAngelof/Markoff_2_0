# client/src/data/reference_store.py
"""
ReferenceStore — фасад для доступа к справочным данным.

Единая точка входа для всех read-only справочников.
Хранит все реестры и управляет их инициализацией.

Используется только в Projections для маппинга ID → DTO.
Не содержит бизнес-логики, только данные.

Пример:
    store = ReferenceStore(api_client)
    store.warmup()
    
    status = store.building_statuses.get(1)
    name = status.name if status else None
"""

# ===== ИМПОРТЫ =====
from src.data.reference.building_status_registry import BuildingStatusRegistry
from src.data.reference.room_status_registry import RoomStatusRegistry
from src.services.api_client import ApiClient
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class ReferenceStore:
    """Фасад для доступа к справочным данным."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, api_client: ApiClient) -> None:
        """Инициализирует фасад (без загрузки данных)."""
        log.system("ReferenceStore инициализация")

        self._building_statuses = BuildingStatusRegistry(api_client)
        self._room_statuses = RoomStatusRegistry(api_client)

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