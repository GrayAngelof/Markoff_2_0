# backend/src/app/structure/service.py
"""
Сервисы для работы с физической структурой (structure).

Предоставляет методы для получения:
- дерева объектов (комплексы → корпуса → этажи → помещения)
- детальной информации по ID
"""

from typing import List, Optional, Type, TypeVar
from sqlmodel import Session, select, func, SQLModel
from utils.logger import get_logger

from .models import Complex, Building, Floor, Room
from .schemas import (
    ComplexTreeSchema,
    BuildingTreeSchema,
    FloorTreeSchema,
    RoomTreeSchema,
    ComplexDetailSchema,
    BuildingDetailSchema,
    FloorDetailSchema,
    RoomDetailSchema,
)

log = get_logger(__name__)

ModelType = TypeVar("ModelType", bound=SQLModel)


# ===== УНИВЕРСАЛЬНАЯ ФУНКЦИЯ ПОДСЧЁТА =====

def _count(
    session: Session, 
    model: Type[ModelType], 
    field_name: str, 
    value: int
) -> int:
    """
    Универсальная функция для подсчёта количества записей.
    """
    filter_column = getattr(model, field_name)
    id_column = getattr(model, "id")  # работает для всех конкретных моделей
    
    stmt = select(func.count(id_column)).where(filter_column == value)
    result = session.execute(stmt)
    return result.scalar_one() or 0


# ===== TREE-МЕТОДЫ (минимальные данные для дерева) =====

def get_complexes_tree(session: Session) -> List[ComplexTreeSchema]:
    """Возвращает все комплексы с количеством корпусов для дерева."""
    log.debug("get_complexes_tree: запрос")
    
    stmt = select(Complex).order_by(Complex.name)
    complexes = session.execute(stmt).scalars().all()
    
    result = []
    for complex_obj in complexes:
        if complex_obj.id is None:
            continue
        buildings_count = _count(session, Building, "complex_id", complex_obj.id)
        result.append(ComplexTreeSchema(
            id=complex_obj.id,
            name=complex_obj.name,
            buildings_count=buildings_count,
        ))
    
    log.info(f"Загружено {len(result)} комплексов")
    return result


def get_buildings_tree(session: Session, complex_id: int) -> List[BuildingTreeSchema]:
    """Возвращает корпуса комплекса с количеством этажей для дерева."""
    log.debug(f"get_buildings_tree: запрос для complex_id={complex_id}")
    
    stmt = select(Building).where(Building.complex_id == complex_id).order_by(Building.name)
    buildings = session.execute(stmt).scalars().all()
    
    result = []
    for building in buildings:
        if building.id is None:
            continue
        floors_count = _count(session, Floor, "building_id", building.id)
        result.append(BuildingTreeSchema(
            id=building.id,
            name=building.name,
            complex_id=building.complex_id,
            floors_count=floors_count,
        ))
    
    log.info(f"Загружено {len(result)} корпусов для комплекса {complex_id}")
    return result


def get_floors_tree(session: Session, building_id: int) -> List[FloorTreeSchema]:
    """Возвращает этажи корпуса с количеством помещений для дерева."""
    log.debug(f"get_floors_tree: запрос для building_id={building_id}")
    
    # type: ignore для Pylance (nullable integer в order_by)
    stmt = select(Floor).where(Floor.building_id == building_id).order_by(Floor.number)  # type: ignore
    floors = session.execute(stmt).scalars().all()
    
    result = []
    for floor in floors:
        if floor.id is None:
            continue
        rooms_count = _count(session, Room, "floor_id", floor.id)
        result.append(FloorTreeSchema(
            id=floor.id,
            number=floor.number,
            building_id=floor.building_id,
            rooms_count=rooms_count,
        ))
    
    log.info(f"Загружено {len(result)} этажей для корпуса {building_id}")
    return result


def get_rooms_tree(session: Session, floor_id: int) -> List[RoomTreeSchema]:
    """Возвращает помещения этажа для дерева."""
    log.debug(f"get_rooms_tree: запрос для floor_id={floor_id}")
    
    # type: ignore для Pylance (nullable string в order_by)
    stmt = select(Room).where(Room.floor_id == floor_id).order_by(Room.number)  # type: ignore
    rooms = session.execute(stmt).scalars().all()
    
    result = []
    for room in rooms:
        if room.id is None:
            continue
        result.append(RoomTreeSchema(
            id=room.id,
            number=room.number,
            floor_id=room.floor_id,
            area=room.area,
        ))
    
    log.info(f"Загружено {len(result)} помещений для этажа {floor_id}")
    return result


# ===== DETAIL-МЕТОДЫ (полные данные для панели) =====

def get_complex_detail(session: Session, complex_id: int) -> Optional[ComplexDetailSchema]:
    """Возвращает детальную информацию о комплексе."""
    log.debug(f"get_complex_detail: запрос для complex_id={complex_id}")
    
    complex_obj = session.get(Complex, complex_id)
    if complex_obj is None or complex_obj.id is None:
        log.warning(f"Комплекс с ID={complex_id} не найден")
        return None
    
    buildings_count = _count(session, Building, "complex_id", complex_obj.id)
    
    return ComplexDetailSchema(
        id=complex_obj.id,
        name=complex_obj.name,
        buildings_count=buildings_count,
        description=complex_obj.description,
        address=complex_obj.address,
        owner_id=complex_obj.owner_id,
        status_id=complex_obj.status_id,
        created_at=complex_obj.created_at,
        updated_at=complex_obj.updated_at,
    )


def get_building_detail(session: Session, building_id: int) -> Optional[BuildingDetailSchema]:
    """Возвращает детальную информацию о корпусе."""
    log.debug(f"get_building_detail: запрос для building_id={building_id}")
    
    building = session.get(Building, building_id)
    if building is None or building.id is None:
        log.warning(f"Корпус с ID={building_id} не найден")
        return None
    
    floors_count = _count(session, Floor, "building_id", building.id)
    
    return BuildingDetailSchema(
        id=building.id,
        name=building.name,
        complex_id=building.complex_id,
        floors_count=floors_count,
        description=building.description,
        address=building.address,
        owner_id=building.owner_id,
        status_id=building.status_id,
        created_at=building.created_at,
        updated_at=building.updated_at,
    )


def get_floor_detail(session: Session, floor_id: int) -> Optional[FloorDetailSchema]:
    """Возвращает детальную информацию об этаже."""
    log.debug(f"get_floor_detail: запрос для floor_id={floor_id}")
    
    floor = session.get(Floor, floor_id)
    if floor is None or floor.id is None:
        log.warning(f"Этаж с ID={floor_id} не найден")
        return None
    
    rooms_count = _count(session, Room, "floor_id", floor.id)
    
    return FloorDetailSchema(
        id=floor.id,
        number=floor.number,
        building_id=floor.building_id,
        rooms_count=rooms_count,
        description=floor.description,
        physical_type_id=floor.physical_type_id,
        status_id=floor.status_id,
        plan_image_url=floor.plan_image_url,
        created_at=floor.created_at,
        updated_at=floor.updated_at,
    )


def get_room_detail(session: Session, room_id: int) -> Optional[RoomDetailSchema]:
    """Возвращает детальную информацию о помещении."""
    log.debug(f"get_room_detail: запрос для room_id={room_id}")
    
    room = session.get(Room, room_id)
    if room is None or room.id is None:
        log.warning(f"Помещение с ID={room_id} не найдено")
        return None
    
    return RoomDetailSchema(
        id=room.id,
        number=room.number,
        floor_id=room.floor_id,
        area=room.area,
        description=room.description,
        physical_type_id=room.physical_type_id,
        status_id=room.status_id,
        max_tenants=room.max_tenants,
        created_at=room.created_at,
        updated_at=room.updated_at,
    )