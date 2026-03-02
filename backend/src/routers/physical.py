# backend/src/routers/physical.py
"""
Роутер для работы с physical данными
Обрабатывает запросы для всех уровней иерархии
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from ..core.deps import get_db
from ..services.physical import (
    get_all_complexes,
    get_buildings_by_complex,
    get_floors_by_building,
    get_rooms_by_floor
)
from ..schemas.physical import (
    ComplexTreeResponse,
    BuildingTreeResponse,
    FloorTreeResponse,
    RoomTreeResponse
)

router = APIRouter(prefix="/physical", tags=["physical"])

# ===== Эндпоинты для комплексов =====
@router.get("/", response_model=List[ComplexTreeResponse])
async def read_complexes(
    db: Session = Depends(get_db)
) -> List[ComplexTreeResponse]:
    """
    Получить список всех комплексов для дерева
    """
    try:
        complexes = get_all_complexes(db)
        return complexes
    except Exception as e:
        print(f"❌ Error in /physical/: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# ===== Эндпоинты для корпусов =====
@router.get("/complexes/{complex_id}/buildings", response_model=List[BuildingTreeResponse])
async def read_buildings(
    complex_id: int,
    db: Session = Depends(get_db)
) -> List[BuildingTreeResponse]:
    """
    Получить список корпусов для конкретного комплекса
    """
    try:
        print(f"🔍 GET /physical/complexes/{complex_id}/buildings")
        buildings = get_buildings_by_complex(db, complex_id)
        print(f"✅ Returning {len(buildings)} buildings")
        return buildings
    except Exception as e:
        print(f"❌ Error in /complexes/{complex_id}/buildings: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# ===== Эндпоинты для этажей =====
@router.get("/buildings/{building_id}/floors", response_model=List[FloorTreeResponse])
async def read_floors(
    building_id: int,
    db: Session = Depends(get_db)
) -> List[FloorTreeResponse]:
    """
    Получить список этажей для конкретного корпуса
    """
    try:
        print(f"🔍 GET /physical/buildings/{building_id}/floors")
        floors = get_floors_by_building(db, building_id)
        print(f"✅ Returning {len(floors)} floors")
        return floors
    except Exception as e:
        print(f"❌ Error in /buildings/{building_id}/floors: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# ===== Эндпоинты для помещений =====
@router.get("/floors/{floor_id}/rooms", response_model=List[RoomTreeResponse])
async def read_rooms(
    floor_id: int,
    db: Session = Depends(get_db)
) -> List[RoomTreeResponse]:
    """
    Получить список помещений для конкретного этажа
    """
    try:
        print(f"🔍 GET /physical/floors/{floor_id}/rooms")
        rooms = get_rooms_by_floor(db, floor_id)
        print(f"✅ Returning {len(rooms)} rooms")
        return rooms
    except Exception as e:
        print(f"❌ Error in /floors/{floor_id}/rooms: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )