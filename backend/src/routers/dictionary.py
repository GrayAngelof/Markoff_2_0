# backend/src/routers/dictionary.py
"""
Роутер для работы со словарями (справочными данными).

Предоставляет эндпоинты для получения статусов зданий и помещений.
"""

# ===== ИМПОРТЫ =====
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.core.deps import get_db
from src.schemas.dictionary import BuildingStatusResponse, RoomStatusResponse
from src.services.dictionary_service import DictionaryService
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)

router = APIRouter(prefix="/dictionary", tags=["dictionary"])


# ===== ЭНДПОИНТЫ =====
@router.get("/building-statuses", response_model=List[BuildingStatusResponse])
def get_building_statuses(db: Session = Depends(get_db)) -> List[BuildingStatusResponse]:
    """
    Получить справочник статусов зданий.

    Returns:
        Список статусов зданий
    """
    log.api("GET /dictionary/building-statuses")
    service = DictionaryService(db)
    return service.get_building_statuses()


@router.get("/room-statuses", response_model=List[RoomStatusResponse])
def get_room_statuses(db: Session = Depends(get_db)) -> List[RoomStatusResponse]:
    """
    Получить справочник статусов помещений.

    Returns:
        Список статусов помещений
    """
    log.api("GET /dictionary/room-statuses")
    service = DictionaryService(db)
    return service.get_room_statuses()