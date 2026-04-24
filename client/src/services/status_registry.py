# client/src/services/status_registry.py
"""
StatusRegistry — runtime-реестр справочников статусов.

Загружает статусы один раз при старте приложения и хранит их в памяти.
Не зависит от DataLoader, UI, контроллеров.

Используется только Projections для маппинга status_id → DTO.

Семантика:
    - warmup() — однократная загрузка при старте
    - get_*() — read-only доступ по ID
    - НЕТ методов обновления (справочники константны на время жизни приложения)
"""

# ===== ИМПОРТЫ =====
from typing import Dict, Optional

from src.models import BuildingStatusDTO, RoomStatusDTO
from src.services.api_client import ApiClient
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class StatusRegistry:
    """
    Реестр статусов (in-memory read-only dataset).

    Пример:
        registry = StatusRegistry(api_client)
        registry.warmup()
        status = registry.get_room_status(1)
        print(status.name)  # "Свободно"
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, api_client: ApiClient) -> None:
        """Инициализирует реестр (без загрузки данных)."""
        log.system("StatusRegistry инициализация")
        self._api = api_client
        self._building_statuses: Dict[int, BuildingStatusDTO] = {}
        self._room_statuses: Dict[int, RoomStatusDTO] = {}
        log.system("StatusRegistry инициализирован (данные не загружены)")

    def warmup(self) -> None:
        """Загружает статусы из API. Вызывается один раз при старте."""
        log.info("Загрузка статусов...")

        building_list = self._api.get_building_statuses()
        room_list = self._api.get_room_statuses()

        self._building_statuses = {s.id: s for s in building_list}
        self._room_statuses = {s.id: s for s in room_list}

        log.success(f"Статусы зданий: {len(self._building_statuses)} записей")
        log.success(f"Статусы помещений: {len(self._room_statuses)} записей")

    # ---- ПУБЛИЧНОЕ API (READ-ONLY) ----
    def get_building_status(self, status_id: Optional[int]) -> Optional[BuildingStatusDTO]:
        """
        Возвращает статус здания по ID.

        Returns:
            None если status_id is None или статус не найден
        """
        if status_id is None:
            return None
        return self._building_statuses.get(status_id)

    def get_room_status(self, status_id: Optional[int]) -> Optional[RoomStatusDTO]:
        """
        Возвращает статус помещения по ID.

        Returns:
            None если status_id is None или статус не найден
        """
        if status_id is None:
            return None
        return self._room_statuses.get(status_id)