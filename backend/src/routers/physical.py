# backend/src/routers/physical.py
"""
Роутер для работы с physical данными
Обрабатывает запросы для всех уровней иерархии
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List, Optional

from ..core.deps import get_db
from ..services.physical_service import PhysicalService
from ..schemas.physical import (
    ComplexTreeResponse,
    BuildingTreeResponse,
    FloorTreeResponse,
    RoomTreeResponse,
    ComplexDetailResponse,
    BuildingDetailResponse,
    FloorDetailResponse,
    RoomDetailResponse
)

from utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/physical", tags=["physical"])


# ===== Эндпоинты для дерева (списки) =====

@router.get("/", response_model=List[ComplexTreeResponse])
async def read_complexes(db: Session = Depends(get_db)):
    """Получить список всех комплексов для дерева"""
    try:
        return PhysicalService.get_complexes(db)
    except Exception as e:
        log.error(f"Ошибка в /physical/: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/complexes/{complex_id}/buildings", response_model=List[BuildingTreeResponse])
async def read_buildings(
    complex_id: int,
    include_owner: bool = Query(False, description="Include owner information"),
    db: Session = Depends(get_db)
):
    """Получить список корпусов для конкретного комплекса"""
    try:
        return PhysicalService.get_buildings(db, complex_id, include_owner)
    except Exception as e:
        log.error(f"Ошибка в /complexes/{complex_id}/buildings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/buildings/{building_id}/floors", response_model=List[FloorTreeResponse])
async def read_floors(
    building_id: int,
    db: Session = Depends(get_db)
):
    """Получить список этажей для конкретного корпуса"""
    try:
        return PhysicalService.get_floors(db, building_id)
    except Exception as e:
        log.error(f"Ошибка в /buildings/{building_id}/floors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/floors/{floor_id}/rooms", response_model=List[RoomTreeResponse])
async def read_rooms(
    floor_id: int,
    db: Session = Depends(get_db)
):
    """Получить список помещений для конкретного этажа"""
    try:
        return PhysicalService.get_rooms(db, floor_id)
    except Exception as e:
        log.error(f"Ошибка в /floors/{floor_id}/rooms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Детальные эндпоинты (для правой панели) =====

@router.get("/complexes/{complex_id}", response_model=ComplexDetailResponse)
async def read_complex_detail(
    complex_id: int,
    include_owner: bool = Query(False, description="Include owner information"),
    db: Session = Depends(get_db)
):
    """Получить детальную информацию о комплексе"""
    try:
        complex_obj = PhysicalService.get_complex(db, complex_id)
        if not complex_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complex not found"
            )
        
        # Подсчитываем количество корпусов
        buildings = PhysicalService.get_buildings(db, complex_id, include_owner=False)
        
        return ComplexDetailResponse(
            id=complex_obj.id,  # type: ignore
            name=complex_obj.name,
            buildings_count=len(buildings),
            description=complex_obj.description,
            address=complex_obj.address,
            owner_id=complex_obj.owner_id,
            created_at=complex_obj.created_at,
            updated_at=complex_obj.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Ошибка в /complexes/{complex_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/buildings/{building_id}", response_model=BuildingDetailResponse)
async def read_building_detail(
    building_id: int,
    include_owner: bool = Query(False, description="Include owner information"),
    db: Session = Depends(get_db)
):
    """Получить детальную информацию о корпусе"""
    try:
        building = PhysicalService.get_building(db, building_id)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Building not found"
            )
        
        # Подсчитываем количество этажей
        floors = PhysicalService.get_floors(db, building_id)
        
        return BuildingDetailResponse(
            id=building.id,  # type: ignore
            name=building.name,
            complex_id=building.complex_id,
            floors_count=len(floors),
            description=building.description,
            address=building.address,
            status_id=building.status_id,
            created_at=building.created_at,
            updated_at=building.updated_at,
            owner_id=building.owner_id
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Ошибка в /buildings/{building_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/floors/{floor_id}", response_model=FloorDetailResponse)
async def read_floor_detail(
    floor_id: int,
    db: Session = Depends(get_db)
):
    """Получить детальную информацию об этаже"""
    try:
        floor = PhysicalService.get_floor(db, floor_id)
        if not floor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Floor not found"
            )
        
        # Подсчитываем количество помещений
        rooms = PhysicalService.get_rooms(db, floor_id)
        
        return FloorDetailResponse(
            id=floor.id,  # type: ignore
            number=floor.number,
            building_id=floor.building_id,
            rooms_count=len(rooms),
            description=floor.description,
            physical_type_id=floor.physical_type_id,
            status_id=floor.status_id,
            plan_image_url=floor.plan_image_url,
            created_at=floor.created_at,
            updated_at=floor.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Ошибка в /floors/{floor_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}", response_model=RoomDetailResponse)
async def read_room_detail(
    room_id: int,
    include_tenant: bool = Query(False, description="Include tenant information"),
    db: Session = Depends(get_db)
):
    """Получить детальную информацию о помещении"""
    try:
        room = PhysicalService.get_room(db, room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )
        
        return RoomDetailResponse(
            id=room.id,  # type: ignore
            number=room.number,
            floor_id=room.floor_id,
            area=room.area,
            status_id=room.status_id,
            description=room.description,
            physical_type_id=room.physical_type_id,
            max_tenants=room.max_tenants,
            created_at=room.created_at,
            updated_at=room.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Ошибка в /rooms/{room_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))