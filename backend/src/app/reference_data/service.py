# backend/src/app/reference_data/service.py
"""
Сервисы для работы со справочниками (reference data).
"""

from typing import List, Type, TypeVar
from sqlmodel import Session, select, asc
from sqlmodel import SQLModel
from pydantic import BaseModel
from utils.logger import get_logger

from .models import (
    BuildingStatus,
    RoomStatus,
    ContractStatus,
    EquipmentStatus,
    PaymentStatus,
    CounterpartyType,
    PlacementStatus,
)
from .schemas import (
    BuildingStatusSchema,
    RoomStatusSchema,
    ContractStatusSchema,
    EquipmentStatusSchema,
    PaymentStatusSchema,
    CounterpartyTypeSchema,
    PlacementStatusSchema,
)

log = get_logger(__name__)

ModelType = TypeVar("ModelType", bound=SQLModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


def _get_all(
    session: Session, 
    model: Type[ModelType], 
    schema: Type[SchemaType],
    model_name: str
) -> List[SchemaType]:
    """
    Универсальная функция для получения всех записей справочника.
    
    Args:
        session: Сессия БД
        model: SQLModel класс
        schema: Pydantic схема
        model_name: Имя модели для логов
    
    Returns:
        Список объектов Pydantic (схем)
    """
    log.debug(f"{model_name}.get_all: запрос")
    
    # Получаем колонку display_order из класса модели
    order_column = getattr(model, "display_order", None)
    if order_column is None:
        # Если display_order нет, сортируем по id
        order_column = getattr(model, "id")
    
    stmt = select(model).order_by(asc(order_column))
    result = session.execute(stmt)
    rows = result.scalars().all()
    
    log.info(f"Загружено {len(rows)} записей из {model_name}")
    return [schema.model_validate(row) for row in rows]


# ===== КОНКРЕТНЫЕ СЕРВИСЫ =====

def get_building_statuses(session: Session) -> List[BuildingStatusSchema]:
    """Возвращает все статусы зданий."""
    return _get_all(session, BuildingStatus, BuildingStatusSchema, "BuildingStatus")


def get_room_statuses(session: Session) -> List[RoomStatusSchema]:
    """Возвращает все статусы помещений."""
    return _get_all(session, RoomStatus, RoomStatusSchema, "RoomStatus")


def get_contract_statuses(session: Session) -> List[ContractStatusSchema]:
    """Возвращает все статусы договоров."""
    return _get_all(session, ContractStatus, ContractStatusSchema, "ContractStatus")


def get_equipment_statuses(session: Session) -> List[EquipmentStatusSchema]:
    """Возвращает все статусы оборудования."""
    return _get_all(session, EquipmentStatus, EquipmentStatusSchema, "EquipmentStatus")


def get_payment_statuses(session: Session) -> List[PaymentStatusSchema]:
    """Возвращает все статусы платежей."""
    return _get_all(session, PaymentStatus, PaymentStatusSchema, "PaymentStatus")


def get_counterparty_types(session: Session) -> List[CounterpartyTypeSchema]:
    """Возвращает все типы контрагентов."""
    return _get_all(session, CounterpartyType, CounterpartyTypeSchema, "CounterpartyType")


def get_placement_statuses(session: Session) -> List[PlacementStatusSchema]:
    """Возвращает все статусы размещения."""
    return _get_all(session, PlacementStatus, PlacementStatusSchema, "PlacementStatus")