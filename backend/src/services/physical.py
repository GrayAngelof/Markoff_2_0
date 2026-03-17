# backend/src/services/physical.py
"""
Сервисный слой для работы с physical схемой
Содержит бизнес-логику для всех уровней иерархии
"""
from sqlmodel import Session, select, func
from typing import List

from ..models.physical import Complex, Building, Floor, Room
from ..schemas.physical import (
    ComplexTreeResponse,
    BuildingTreeResponse,
    FloorTreeResponse,
    RoomTreeResponse
)

from utils.logger import get_logger

log = get_logger(__name__)


# ===== Сервисы для комплексов =====
def get_all_complexes(db: Session) -> List[ComplexTreeResponse]:
    """
    Получить список всех комплексов для отображения в дереве
    """
    try:
        complexes = db.exec(select(Complex)).all()
        result = []

        for complex_obj in complexes:
            # ИСПРАВЛЕНО: игнорируем проверку типа для ID
            count_result = db.exec(
                select(func.count(Building.id)).where(Building.complex_id == complex_obj.id)  # type: ignore
            ).first()
            
            buildings_count = 0
            if count_result is not None:
                if isinstance(count_result, tuple) and len(count_result) > 0:
                    buildings_count = int(count_result[0])
                else:
                    buildings_count = int(count_result)
            
            result.append(ComplexTreeResponse(
                id=complex_obj.id,  # type: ignore
                name=complex_obj.name,
                buildings_count=buildings_count
            ))
        
        log.info(f"Сервис: загружено {len(result)} комплексов")
        return result
        
    except Exception as e:
        log.error(f"Ошибка в сервисе get_all_complexes: {e}")
        raise


# ===== Сервисы для корпусов =====
def get_buildings_by_complex(db: Session, complex_id: int) -> List[BuildingTreeResponse]:
    """
    Получить список корпусов для конкретного комплекса
    """
    try:
        buildings = db.exec(
            select(Building).where(Building.complex_id == complex_id)
        ).all()
        
        result = []
        for building in buildings:
            # ИСПРАВЛЕНО: игнорируем проверку типа для ID
            count_result = db.exec(
                select(func.count(Floor.id)).where(Floor.building_id == building.id)  # type: ignore
            ).first()
            
            floors_count = 0
            if count_result is not None:
                if isinstance(count_result, tuple) and len(count_result) > 0:
                    floors_count = int(count_result[0])
                else:
                    floors_count = int(count_result)
            
            result.append(BuildingTreeResponse(
                id=building.id,  # type: ignore
                name=building.name,
                complex_id=building.complex_id,
                floors_count=floors_count,
                owner_id=building.owner_id
            ))
        
        log.info(f"Сервис: загружено {len(result)} корпусов для комплекса {complex_id}")
        return result
        
    except Exception as e:
        log.error(f"Ошибка в сервисе get_buildings_by_complex: {e}")
        raise


# ===== Сервисы для этажей =====
def get_floors_by_building(db: Session, building_id: int) -> List[FloorTreeResponse]:
    """
    Получить список этажей для конкретного корпуса
    """
    try:
        floors = db.exec(
            select(Floor)
            .where(Floor.building_id == building_id)
            .order_by(Floor.number)  # type: ignore
        ).all()
        
        result = []
        for floor in floors:
            # ИСПРАВЛЕНО: игнорируем проверку типа для ID
            count_result = db.exec(
                select(func.count(Room.id)).where(Room.floor_id == floor.id)  # type: ignore
            ).first()
            
            rooms_count = 0
            if count_result is not None:
                if isinstance(count_result, tuple) and len(count_result) > 0:
                    rooms_count = int(count_result[0])
                else:
                    rooms_count = int(count_result)
            
            result.append(FloorTreeResponse(
                id=floor.id,  # type: ignore
                number=floor.number,
                building_id=floor.building_id,
                rooms_count=rooms_count
            ))
        
        log.info(f"Сервис: загружено {len(result)} этажей для корпуса {building_id}")
        return result
        
    except Exception as e:
        log.error(f"Ошибка в сервисе get_floors_by_building: {e}")
        raise


# ===== Сервисы для помещений =====
def get_rooms_by_floor(db: Session, floor_id: int) -> List[RoomTreeResponse]:
    """
    Получить список помещений для конкретного этажа
    """
    try:
        rooms = db.exec(
            select(Room)
            .where(Room.floor_id == floor_id)
            .order_by(Room.number)  # type: ignore
        ).all()
        
        result = []
        for room in rooms:
            result.append(RoomTreeResponse(
                id=room.id,  # type: ignore
                number=room.number,
                floor_id=room.floor_id,
                area=room.area,
                status_code=room.status_code
            ))
        
        log.info(f"Сервис: загружено {len(result)} помещений для этажа {floor_id}")
        return result
        
    except Exception as e:
        log.error(f"Ошибка в сервисе get_rooms_by_floor: {e}")
        raise