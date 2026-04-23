# backend/src/services/dictionary_service.py
"""
Сервисы для работы со справочными данными (схема dictionary).

Предоставляет методы для получения статусов зданий и помещений.
"""

# ===== ИМПОРТЫ =====
from typing import List

from sqlmodel import Session, asc, select

from src.models.dictionary import BuildingStatus, RoomStatus
from src.schemas.dictionary import BuildingStatusResponse, RoomStatusResponse
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАССЫ =====
class DictionaryService:
    """Сервис для работы со справочниками."""

    def __init__(self, session: Session) -> None:
        """Инициализирует сервис с сессией БД."""
        self._session = session

    def get_building_statuses(self) -> List[BuildingStatusResponse]:
        """
        Возвращает все статусы зданий.

        Returns:
            Список статусов, отсортированный по id
        """
        log.debug("DictionaryService.get_building_statuses: запрос")
        query = select(BuildingStatus).order_by(asc(BuildingStatus.id))
        result = self._session.execute(query)
        statuses = result.scalars().all()

        log.info(f"Загружено {len(statuses)} статусов зданий")
        return [BuildingStatusResponse.model_validate(s) for s in statuses]

    def get_room_statuses(self) -> List[RoomStatusResponse]:
        """
        Возвращает все статусы помещений.

        Returns:
            Список статусов, отсортированный по id
        """
        log.debug("DictionaryService.get_room_statuses: запрос")
        query = select(RoomStatus).order_by(asc(RoomStatus.id))
        result = self._session.execute(query)
        statuses = result.scalars().all()

        log.info(f"Загружено {len(statuses)} статусов помещений")
        return [RoomStatusResponse.model_validate(s) for s in statuses]