# backend/src/services/dictionary_service.py
"""
Сервисы для работы с dictionary схемой
"""

from sqlmodel import Session, select, asc
from typing import List

from utils.logger import get_logger
from ..models.dictionary import BuildingStatus, RoomStatus
from ..schemas.dictionary import BuildingStatusResponse, RoomStatusResponse

log = get_logger(__name__)


class DictionaryService:
    """Сервис для работы со справочниками"""

    def __init__(self, session: Session):
        """Инициализация сервиса с сессией БД"""
        self._session = session

    def get_building_statuses(self) -> List[BuildingStatusResponse]:
        """
        Получить все статусы зданий.
        
        Returns:
            List[BuildingStatusResponse]: список статусов, отсортированный по id
        """
        log.debug("DictionaryService.get_building_statuses: запрос")
        query = select(BuildingStatus).order_by(asc(BuildingStatus.id))
        result = self._session.execute(query)
        statuses = result.scalars().all()
        
        log.info(f"Загружено {len(statuses)} статусов зданий")
        return [BuildingStatusResponse.model_validate(s) for s in statuses]

    def get_room_statuses(self) -> List[RoomStatusResponse]:
        """
        Получить все статусы помещений.
        
        Returns:
            List[RoomStatusResponse]: список статусов, отсортированный по id
        """
        log.debug("DictionaryService.get_room_statuses: запрос")
        query = select(RoomStatus).order_by(asc(RoomStatus.id))
        result = self._session.execute(query)
        statuses = result.scalars().all()
        
        log.info(f"Загружено {len(statuses)} статусов помещений")
        return [RoomStatusResponse.model_validate(s) for s in statuses]