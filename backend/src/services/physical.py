# backend/src/services/physical.py
"""
Сервисный слой для работы с physical схемой
Содержит бизнес-логику для всех уровней иерархии
"""
from sqlmodel import Session, select, func
from typing import List, Optional

from ..models.physical import Complex, Building, Floor, Room
from ..schemas.physical import (
    ComplexTreeResponse, 
    BuildingTreeResponse, 
    FloorTreeResponse, 
    RoomTreeResponse
)

# ===== Сервисы для комплексов =====
def get_all_complexes(db: Session) -> List[ComplexTreeResponse]:
    """
    Получить список всех комплексов для отображения в дереве
    
    Returns:
        List[ComplexTreeResponse]: список комплексов с количеством корпусов
    """
    try:
        # Формируем запрос с подсчётом корпусов
        statement = select(
            Complex.id,
            Complex.name,
            func.count(Building.id).label("buildings_count")
        ).outerjoin(
            Building, Building.complex_id == Complex.id
        ).group_by(
            Complex.id, Complex.name
        ).order_by(Complex.name)
        
        result = db.exec(statement)
        
        # Преобразуем результат в список словарей
        complexes = []
        for row in result:
            complexes.append(ComplexTreeResponse(
                id=row.id,
                name=row.name,
                buildings_count=row.buildings_count
            ))
        
        return complexes
    except Exception as e:
        print(f"❌ Error in get_all_complexes: {e}")
        raise

# ===== Сервисы для корпусов =====
def get_buildings_by_complex(db: Session, complex_id: int) -> List[BuildingTreeResponse]:
    """
    Получить список корпусов для конкретного комплекса
    
    Args:
        complex_id: ID комплекса
        
    Returns:
        List[BuildingTreeResponse]: список корпусов с количеством этажей
    """
    try:
        print(f"🔍 Fetching buildings for complex_id: {complex_id}")
        
        # Сначала проверим, есть ли вообще корпуса для этого комплекса
        buildings_check = select(Building).where(Building.complex_id == complex_id)
        buildings_result = db.exec(buildings_check).all()
        print(f"📊 Found {len(buildings_result)} buildings in complex {complex_id}")
        
        # Запрос с подсчётом этажей
        statement = select(
            Building.id,
            Building.name,
            Building.complex_id,
            func.count(Floor.id).label("floors_count")
        ).outerjoin(
            Floor, Floor.building_id == Building.id
        ).where(
            Building.complex_id == complex_id
        ).group_by(
            Building.id, Building.name, Building.complex_id
        ).order_by(Building.name)
        
        print(f"📝 Executing query: {statement}")
        result = db.exec(statement)
        
        buildings = []
        for row in result:
            print(f"✅ Found building: id={row.id}, name={row.name}, floors={row.floors_count}")
            buildings.append(BuildingTreeResponse(
                id=row.id,
                name=row.name,
                complex_id=row.complex_id,
                floors_count=row.floors_count
            ))
        
        return buildings
    except Exception as e:
        print(f"❌ Error in get_buildings_by_complex: {e}")
        import traceback
        traceback.print_exc()
        raise

# ===== Сервисы для этажей =====
def get_floors_by_building(db: Session, building_id: int) -> List[FloorTreeResponse]:
    """
    Получить список этажей для конкретного корпуса
    
    Args:
        building_id: ID корпуса
        
    Returns:
        List[FloorTreeResponse]: список этажей с количеством помещений
    """
    try:
        print(f"🔍 Fetching floors for building_id: {building_id}")
        
        # Проверяем существование корпуса
        building_exists = db.get(Building, building_id)
        if not building_exists:
            print(f"⚠️ Building {building_id} not found")
            return []
        
        # Запрос с подсчётом помещений
        statement = select(
            Floor.id,
            Floor.number,
            Floor.building_id,
            func.count(Room.id).label("rooms_count")
        ).outerjoin(
            Room, Room.floor_id == Floor.id
        ).where(
            Floor.building_id == building_id
        ).group_by(
            Floor.id, Floor.number, Floor.building_id
        ).order_by(Floor.number)
        
        result = db.exec(statement)
        
        floors = []
        for row in result:
            print(f"✅ Found floor: id={row.id}, number={row.number}, rooms={row.rooms_count}")
            floors.append(FloorTreeResponse(
                id=row.id,
                number=row.number,
                building_id=row.building_id,
                rooms_count=row.rooms_count
            ))
        
        return floors
    except Exception as e:
        print(f"❌ Error in get_floors_by_building: {e}")
        import traceback
        traceback.print_exc()
        raise

# ===== Сервисы для помещений =====
def get_rooms_by_floor(db: Session, floor_id: int) -> List[RoomTreeResponse]:
    """
    Получить список помещений для конкретного этажа
    
    Args:
        floor_id: ID этажа
        
    Returns:
        List[RoomTreeResponse]: список помещений
    """
    try:
        print(f"🔍 Fetching rooms for floor_id: {floor_id}")
        
        # Проверяем существование этажа
        floor_exists = db.get(Floor, floor_id)
        if not floor_exists:
            print(f"⚠️ Floor {floor_id} not found")
            return []
        
        # Запрос помещений
        statement = select(
            Room.id,
            Room.number,
            Room.floor_id,
            Room.area,
            Room.status_code
        ).where(
            Room.floor_id == floor_id
        ).order_by(Room.number)
        
        result = db.exec(statement)
        
        rooms = []
        for row in result:
            print(f"✅ Found room: id={row.id}, number={row.number}")
            rooms.append(RoomTreeResponse(
                id=row.id,
                number=row.number,
                floor_id=row.floor_id,
                area=row.area,
                status_code=row.status_code
            ))
        
        return rooms
    except Exception as e:
        print(f"❌ Error in get_rooms_by_floor: {e}")
        import traceback
        traceback.print_exc()
        raise