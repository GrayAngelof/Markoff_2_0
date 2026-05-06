# backend/src/app/reference_data/router.py
"""
Роутер для работы со справочниками (reference data).

Предоставляет эндпоинты для получения всех справочников:
- статусы зданий, помещений, договоров, оборудования, платежей, размещения
- типы контрагентов
"""

# ===== ИМПОРТЫ =====
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.infrastructure.deps import get_db
from src.app.reference_data.service import (
    get_building_statuses,
    get_room_statuses,
    get_contract_statuses,
    get_equipment_statuses,
    get_payment_statuses,
    get_counterparty_types,
    get_placement_statuses,
)
from src.app.reference_data.schemas import (
    BuildingStatusSchema,
    RoomStatusSchema,
    ContractStatusSchema,
    EquipmentStatusSchema,
    PaymentStatusSchema,
    CounterpartyTypeSchema,
    PlacementStatusSchema,
)
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)

router = APIRouter(prefix="/reference-data", tags=["reference-data"])


# ===== ЭНДПОИНТЫ =====
@router.get("/building-statuses", response_model=List[BuildingStatusSchema])
def get_building_statuses_endpoint(db: Session = Depends(get_db)) -> List[BuildingStatusSchema]:
    """
    Получить справочник статусов зданий.
    
    Returns:
        Список статусов зданий с полями:
        id, code, name, description, display_order, created_at, updated_at,
        is_initial, allows_occupancy
    """
    log.api("GET /reference-data/building-statuses")
    return get_building_statuses(db)


@router.get("/room-statuses", response_model=List[RoomStatusSchema])
def get_room_statuses_endpoint(db: Session = Depends(get_db)) -> List[RoomStatusSchema]:
    """
    Получить справочник статусов помещений.
    
    Returns:
        Список статусов помещений с полями:
        id, code, name, description, display_order, created_at, updated_at,
        is_initial, allows_rent
    """
    log.api("GET /reference-data/room-statuses")
    return get_room_statuses(db)


@router.get("/contract-statuses", response_model=List[ContractStatusSchema])
def get_contract_statuses_endpoint(db: Session = Depends(get_db)) -> List[ContractStatusSchema]:
    """
    Получить справочник статусов договоров.
    
    Returns:
        Список статусов договоров с полями:
        id, code, name, description, display_order, created_at, updated_at,
        is_initial, is_terminal
    """
    log.api("GET /reference-data/contract-statuses")
    return get_contract_statuses(db)


@router.get("/equipment-statuses", response_model=List[EquipmentStatusSchema])
def get_equipment_statuses_endpoint(db: Session = Depends(get_db)) -> List[EquipmentStatusSchema]:
    """
    Получить справочник статусов оборудования.
    
    Returns:
        Список статусов оборудования с полями:
        id, code, name, description, display_order, created_at, updated_at,
        is_initial, is_operational
    """
    log.api("GET /reference-data/equipment-statuses")
    return get_equipment_statuses(db)


@router.get("/payment-statuses", response_model=List[PaymentStatusSchema])
def get_payment_statuses_endpoint(db: Session = Depends(get_db)) -> List[PaymentStatusSchema]:
    """
    Получить справочник статусов платежей.
    
    Returns:
        Список статусов платежей с полями:
        id, code, name, description, display_order, created_at, updated_at,
        is_initial, is_success
    """
    log.api("GET /reference-data/payment-statuses")
    return get_payment_statuses(db)


@router.get("/counterparty-types", response_model=List[CounterpartyTypeSchema])
def get_counterparty_types_endpoint(db: Session = Depends(get_db)) -> List[CounterpartyTypeSchema]:
    """
    Получить справочник типов контрагентов.
    
    Returns:
        Список типов контрагентов с полями:
        id, code, name, description, display_order, created_at, updated_at,
        is_active
    """
    log.api("GET /reference-data/counterparty-types")
    return get_counterparty_types(db)


@router.get("/placement-statuses", response_model=List[PlacementStatusSchema])
def get_placement_statuses_endpoint(db: Session = Depends(get_db)) -> List[PlacementStatusSchema]:
    """
    Получить справочник статусов размещения.
    
    Returns:
        Список статусов размещения с полями:
        id, code, name, description, display_order, created_at, updated_at,
        is_initial
    """
    log.api("GET /reference-data/placement-statuses")
    return get_placement_statuses(db)