# backend/src/app/structure/router.py
"""
Роутер для работы с физической структурой (structure).

Обрабатывает запросы для всех уровней иерархии:
- комплексы (complexes)
- корпуса (buildings)
- этажи (floors)
- помещения (rooms)

Поддерживает как tree-эндпоинты (для дерева), так и detail-эндпоинты (для панели).
"""

# ===== ИМПОРТЫ =====
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.infrastructure.deps import get_db
from src.app.structure.service import (
    get_complexes_tree,
    get_buildings_tree,
    get_floors_tree,
    get_rooms_tree,
    get_complex_detail,
    get_building_detail,
    get_floor_detail,
    get_room_detail,
)
from src.app.structure.schemas import (
    ComplexTreeSchema,
    BuildingTreeSchema,
    FloorTreeSchema,
    RoomTreeSchema,
    ComplexDetailSchema,
    BuildingDetailSchema,
    FloorDetailSchema,
    RoomDetailSchema,
)
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)

router = APIRouter(prefix="/physical", tags=["physical"])


# ===== TREE-ЭНДПОИНТЫ (минимальные данные для дерева) =====

@router.get("/complexes", response_model=List[ComplexTreeSchema])
def get_complexes(db: Session = Depends(get_db)) -> List[ComplexTreeSchema]:
    """
    Получить список всех комплексов для дерева.
    
    Returns:
        Список комплексов с количеством корпусов
    """
    log.api("GET /physical/complexes")
    return get_complexes_tree(db)


@router.get("/complexes/{complex_id}/buildings", response_model=List[BuildingTreeSchema])
def get_buildings(
    complex_id: int,
    db: Session = Depends(get_db)
) -> List[BuildingTreeSchema]:
    """
    Получить список корпусов для конкретного комплекса.
    
    Args:
        complex_id: ID комплекса
    
    Returns:
        Список корпусов с количеством этажей
    """
    log.api(f"GET /physical/complexes/{complex_id}/buildings")
    return get_buildings_tree(db, complex_id)


@router.get("/buildings/{building_id}/floors", response_model=List[FloorTreeSchema])
def get_floors(
    building_id: int,
    db: Session = Depends(get_db)
) -> List[FloorTreeSchema]:
    """
    Получить список этажей для конкретного корпуса.
    
    Args:
        building_id: ID корпуса
    
    Returns:
        Список этажей с количеством помещений
    """
    log.api(f"GET /physical/buildings/{building_id}/floors")
    return get_floors_tree(db, building_id)


@router.get("/floors/{floor_id}/rooms", response_model=List[RoomTreeSchema])
def get_rooms(
    floor_id: int,
    db: Session = Depends(get_db)
) -> List[RoomTreeSchema]:
    """
    Получить список помещений для конкретного этажа.
    
    Args:
        floor_id: ID этажа
    
    Returns:
        Список помещений
    """
    log.api(f"GET /physical/floors/{floor_id}/rooms")
    return get_rooms_tree(db, floor_id)


# ===== DETAIL-ЭНДПОИНТЫ (полные данные для панели) =====

@router.get("/complexes/{complex_id}", response_model=ComplexDetailSchema)
def get_complex_detail_endpoint(
    complex_id: int,
    db: Session = Depends(get_db)
) -> ComplexDetailSchema:
    """
    Получить детальную информацию о комплексе.
    
    Args:
        complex_id: ID комплекса
    
    Returns:
        Полная информация о комплексе
    
    Raises:
        HTTPException 404: если комплекс не найден
    """
    log.api(f"GET /physical/complexes/{complex_id}")
    
    complex_detail = get_complex_detail(db, complex_id)
    if complex_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комплекс с ID={complex_id} не найден"
        )
    
    return complex_detail


@router.get("/buildings/{building_id}", response_model=BuildingDetailSchema)
def get_building_detail_endpoint(
    building_id: int,
    db: Session = Depends(get_db)
) -> BuildingDetailSchema:
    """
    Получить детальную информацию о корпусе.
    
    Args:
        building_id: ID корпуса
    
    Returns:
        Полная информация о корпусе
    
    Raises:
        HTTPException 404: если корпус не найден
    """
    log.api(f"GET /physical/buildings/{building_id}")
    
    building_detail = get_building_detail(db, building_id)
    if building_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Корпус с ID={building_id} не найден"
        )
    
    return building_detail


@router.get("/floors/{floor_id}", response_model=FloorDetailSchema)
def get_floor_detail_endpoint(
    floor_id: int,
    db: Session = Depends(get_db)
) -> FloorDetailSchema:
    """
    Получить детальную информацию об этаже.
    
    Args:
        floor_id: ID этажа
    
    Returns:
        Полная информация об этаже
    
    Raises:
        HTTPException 404: если этаж не найден
    """
    log.api(f"GET /physical/floors/{floor_id}")
    
    floor_detail = get_floor_detail(db, floor_id)
    if floor_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Этаж с ID={floor_id} не найден"
        )
    
    return floor_detail


@router.get("/rooms/{room_id}", response_model=RoomDetailSchema)
def get_room_detail_endpoint(
    room_id: int,
    db: Session = Depends(get_db)
) -> RoomDetailSchema:
    """
    Получить детальную информацию о помещении.
    
    Args:
        room_id: ID помещения
    
    Returns:
        Полная информация о помещении
    
    Raises:
        HTTPException 404: если помещение не найдено
    """
    log.api(f"GET /physical/rooms/{room_id}")
    
    room_detail = get_room_detail(db, room_id)
    if room_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Помещение с ID={room_id} не найдено"
        )
    
    return room_detail