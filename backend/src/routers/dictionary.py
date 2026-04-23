# backend/src/routers/dictionary.py
"""
Роутер для работы со словарями
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional

from ..core.deps import get_db
from ..services.dictionary_service import DictionaryService
from ..schemas.dictionary import BuildingStatusResponse, RoomStatusResponse

from utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/dictionary", tags=["dictionary"])


@router.get("/building-statuses", response_model=List[BuildingStatusResponse])
def get_building_statuses(
    db: Session = Depends(get_db),
) -> List[BuildingStatusResponse]:
    """
    Получить справочник статусов зданий.
    
    Returns:
        List[BuildingStatusResponse]: список статусов зданий
    """
    log.api("GET /dictionary/building-statuses")
    service = DictionaryService(db)
    return service.get_building_statuses()


@router.get("/room-statuses", response_model=List[RoomStatusResponse])
def get_room_statuses(
    db: Session = Depends(get_db),
) -> List[RoomStatusResponse]:
    """
    Получить справочник статусов помещений.
    
    Returns:
        List[RoomStatusResponse]: список статусов помещений
    """
    log.api("GET /dictionary/room-statuses")
    service = DictionaryService(db)
    return service.get_room_statuses()