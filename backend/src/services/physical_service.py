# backend/src/services/physical_service.py
"""
Сервисы для работы с physical схемой
Явные запросы с правильной обработкой типов
"""
from sqlmodel import Session, select, func
from typing import List, Optional

from ..models.physical import Complex, Building, Floor, Room
from ..models.dictionary import Counterparty
from ..schemas.physical import (
    ComplexTreeResponse,
    BuildingTreeResponse,
    FloorTreeResponse,
    RoomTreeResponse
)

from utils.logger import get_logger

log = get_logger(__name__)


class PhysicalService:
    """Сервис для работы с физической структурой"""
    
    # ===== Методы для получения единичных объектов =====
    
    @staticmethod
    def get_complex(db: Session, complex_id: int) -> Optional[Complex]:
        """Получить комплекс по ID"""
        return db.get(Complex, complex_id)
    
    @staticmethod
    def get_building(db: Session, building_id: int) -> Optional[Building]:
        """Получить корпус по ID"""
        return db.get(Building, building_id)
    
    @staticmethod
    def get_floor(db: Session, floor_id: int) -> Optional[Floor]:
        """Получить этаж по ID"""
        return db.get(Floor, floor_id)
    
    @staticmethod
    def get_room(db: Session, room_id: int) -> Optional[Room]:
        """Получить помещение по ID"""
        return db.get(Room, room_id)
    
    # ===== Методы для получения списков =====
    
    @staticmethod
    def get_complexes(db: Session) -> List[ComplexTreeResponse]:
        """Получить все комплексы с количеством корпусов"""
        try:
            complexes = db.exec(select(Complex)).all()
            result = []
            
            for complex_obj in complexes:
                # Явный подсчёт корпусов с обработкой None
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
            log.error(f"Ошибка в сервисе get_complexes: {e}")
            raise
    
    @staticmethod
    def get_buildings(db: Session, complex_id: int, include_owner: bool = False) -> List[BuildingTreeResponse]:
        """Получить корпуса с количеством этажей"""
        try:
            buildings = db.exec(
                select(Building).where(Building.complex_id == complex_id)
            ).all()
            
            result = []
            for building in buildings:
                # Явный подсчёт этажей
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
                ))
            
            log.info(f"Сервис: загружено {len(result)} корпусов для комплекса {complex_id}")
            return result
            
        except Exception as e:
            log.error(f"Ошибка в сервисе get_buildings: {e}")
            raise
    
    @staticmethod
    def get_floors(db: Session, building_id: int) -> List[FloorTreeResponse]:
        """Получить этажи с количеством помещений"""
        try:
            floors = db.exec(
                select(Floor)
                .where(Floor.building_id == building_id)
                .order_by(Floor.number)  # type: ignore
            ).all()
            
            result = []
            for floor in floors:
                # Явный подсчёт помещений
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
            log.error(f"Ошибка в сервисе get_floors: {e}")
            raise
    
    @staticmethod
    def get_rooms(db: Session, floor_id: int) -> List[RoomTreeResponse]:
        """Получить помещения этажа"""
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
                ))
            
            log.info(f"Сервис: загружено {len(result)} помещений для этажа {floor_id}")
            return result
            
        except Exception as e:
            log.error(f"Ошибка в сервисе get_rooms: {e}")
            raise