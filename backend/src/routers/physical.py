# backend/src/routers/physical.py
"""
Роутер для работы с physical данными
Обрабатывает запросы для всех уровней иерархии
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from typing import List, Optional

from ..core.deps import get_db
from ..models.physical import Complex, Building, Floor, Room
from ..models.dictionary.counterparty import Counterparty
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


# ===== Вспомогательные функции =====
def _load_owner(db: Session, owner_id: Optional[int]) -> Optional[dict]:
    """Загружает данные владельца по ID и преобразует в словарь."""
    if owner_id is None:
        return None
    
    owner_obj = db.get(Counterparty, owner_id)
    if not owner_obj:
        log.warning(f"Владелец с ID {owner_id} не найден")
        return None
    
    if hasattr(owner_obj, 'model_dump'):
        return owner_obj.model_dump()
    
    return {
        "id": owner_obj.id,
        "short_name": owner_obj.short_name,
        "tax_id": owner_obj.tax_id,
        "full_name": owner_obj.full_name,
        "legal_address": owner_obj.legal_address,
        "actual_address": owner_obj.actual_address,
        "bank_details": owner_obj.bank_details
    }


# ===== Эндпоинты для комплексов (дерево) =====
@router.get("/", response_model=List[ComplexTreeResponse])
async def read_complexes(db: Session = Depends(get_db)) -> List[ComplexTreeResponse]:
    """Получить список всех комплексов для дерева"""
    try:
        complexes = db.exec(select(Complex)).all()
        result: List[ComplexTreeResponse] = []

        for complex_obj in complexes:
            # ИСПРАВЛЕНО: используем first() вместо scalar_one()
            count_result = db.exec(
                select(func.count(Building.id)).where(Building.complex_id == complex_obj.id)  # type: ignore
            ).first()
            
            # ИСПРАВЛЕНО: явно преобразуем в int
            buildings_count = 0
            if count_result is not None:
                if isinstance(count_result, tuple) and len(count_result) > 0:
                    buildings_count = int(count_result[0])
                else:
                    buildings_count = int(count_result)
            
            result.append(
                ComplexTreeResponse(
                    id=complex_obj.id,  # type: ignore
                    name=complex_obj.name,
                    buildings_count=buildings_count
                )
            )
        
        log.info(f"Загружено {len(result)} комплексов")
        return result
        
    except Exception as e:
        log.error(f"Ошибка загрузки комплексов: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== Эндпоинты для корпусов (дерево) =====
@router.get("/complexes/{complex_id}/buildings", response_model=List[BuildingTreeResponse])
async def read_buildings(
    complex_id: int,
    include_owner: bool = Query(False, description="Include owner information"),
    db: Session = Depends(get_db)
) -> List[BuildingTreeResponse]:
    """Получить список корпусов для конкретного комплекса"""
    try:
        buildings = db.exec(
            select(Building).where(Building.complex_id == complex_id)
        ).all()
        
        result: List[BuildingTreeResponse] = []

        for building in buildings:
            # ИСПРАВЛЕНО: используем first() вместо scalar_one()
            count_result = db.exec(
                select(func.count(Floor.id)).where(Floor.building_id == building.id)  # type: ignore
            ).first()
            
            floors_count = 0
            if count_result is not None:
                if isinstance(count_result, tuple) and len(count_result) > 0:
                    floors_count = int(count_result[0])
                else:
                    floors_count = int(count_result)
            
            owner_data = None
            if include_owner:
                owner_data = _load_owner(db, building.owner_id)
            
            result.append(
                BuildingTreeResponse(
                    id=building.id,  # type: ignore
                    name=building.name,
                    complex_id=building.complex_id,
                    floors_count=floors_count,
                    owner_id=building.owner_id,
                    owner=owner_data
                )
            )
        
        log.info(f"Загружено {len(result)} корпусов для комплекса {complex_id}")
        return result
        
    except Exception as e:
        log.error(f"Ошибка загрузки корпусов для комплекса {complex_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== Эндпоинты для этажей (дерево) =====
@router.get("/buildings/{building_id}/floors", response_model=List[FloorTreeResponse])
async def read_floors(
    building_id: int,
    db: Session = Depends(get_db)
) -> List[FloorTreeResponse]:
    """Получить список этажей для конкретного корпуса"""
    try:
        floors = db.exec(
            select(Floor)
            .where(Floor.building_id == building_id)
            .order_by(Floor.number)  # type: ignore
        ).all()
        
        result: List[FloorTreeResponse] = []

        for floor in floors:
            # ИСПРАВЛЕНО: используем first() вместо scalar_one()
            count_result = db.exec(
                select(func.count(Room.id)).where(Room.floor_id == floor.id)  # type: ignore
            ).first()
            
            rooms_count = 0
            if count_result is not None:
                if isinstance(count_result, tuple) and len(count_result) > 0:
                    rooms_count = int(count_result[0])
                else:
                    rooms_count = int(count_result)
            
            result.append(
                FloorTreeResponse(
                    id=floor.id,  # type: ignore
                    number=floor.number,
                    building_id=floor.building_id,
                    rooms_count=rooms_count
                )
            )
        
        log.info(f"Загружено {len(result)} этажей для корпуса {building_id}")
        return result
        
    except Exception as e:
        log.error(f"Ошибка загрузки этажей для корпуса {building_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== Эндпоинты для помещений (дерево) =====
@router.get("/floors/{floor_id}/rooms", response_model=List[RoomTreeResponse])
async def read_rooms(
    floor_id: int,
    db: Session = Depends(get_db)
) -> List[RoomTreeResponse]:
    """Получить список помещений для конкретного этажа"""
    try:
        rooms = db.exec(
            select(Room)
            .where(Room.floor_id == floor_id)
            .order_by(Room.number)  # type: ignore
        ).all()
        
        result: List[RoomTreeResponse] = []

        for room in rooms:
            result.append(
                RoomTreeResponse(
                    id=room.id,  # type: ignore
                    number=room.number,
                    floor_id=room.floor_id,
                    area=room.area,
                    status_code=room.status_code
                )
            )
        
        log.info(f"Загружено {len(result)} помещений для этажа {floor_id}")
        return result
        
    except Exception as e:
        log.error(f"Ошибка загрузки помещений для этажа {floor_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== Детальные эндпоинты для правой панели =====
@router.get("/complexes/{complex_id}", response_model=ComplexDetailResponse)
async def read_complex_detail(
    complex_id: int,
    include_owner: bool = Query(False, description="Include owner information"),
    db: Session = Depends(get_db)
) -> ComplexDetailResponse:
    """Получить детальную информацию о комплексе"""
    try:
        complex_obj = db.get(Complex, complex_id)
        if not complex_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complex not found"
            )
        
        # ИСПРАВЛЕНО: используем first() вместо scalar_one()
        count_result = db.exec(
            select(func.count(Building.id)).where(Building.complex_id == complex_id) # type: ignore
        ).first()
        
        buildings_count = 0
        if count_result is not None:
            if isinstance(count_result, tuple) and len(count_result) > 0:
                buildings_count = int(count_result[0])
            else:
                buildings_count = int(count_result)
        
        owner_data = _load_owner(db, complex_obj.owner_id) if include_owner else None

        log.info(f"Загружены детали комплекса {complex_id}")
        
        return ComplexDetailResponse(
            id=complex_obj.id,  # type: ignore
            name=complex_obj.name,
            buildings_count=buildings_count,
            description=complex_obj.description,
            address=complex_obj.address,
            owner_id=complex_obj.owner_id,
            created_at=complex_obj.created_at,
            updated_at=complex_obj.updated_at,
            owner=owner_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Ошибка загрузки деталей комплекса {complex_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/buildings/{building_id}", response_model=BuildingDetailResponse)
async def read_building_detail(
    building_id: int,
    include_owner: bool = Query(False, description="Include owner information"),
    db: Session = Depends(get_db)
) -> BuildingDetailResponse:
    """Получить детальную информацию о корпусе"""
    try:
        building = db.get(Building, building_id)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Building not found"
            )
        
        # ИСПРАВЛЕНО: используем first() вместо scalar_one()
        count_result = db.exec(
            select(func.count(Floor.id)).where(Floor.building_id == building_id) # type: ignore
        ).first()
        
        floors_count = 0
        if count_result is not None:
            if isinstance(count_result, tuple) and len(count_result) > 0:
                floors_count = int(count_result[0])
            else:
                floors_count = int(count_result)
        
        owner_data = _load_owner(db, building.owner_id) if include_owner else None

        log.info(f"Загружены детали корпуса {building_id}")
        
        return BuildingDetailResponse(
            id=building.id,  # type: ignore
            name=building.name,
            complex_id=building.complex_id,
            floors_count=floors_count,
            description=building.description,
            address=building.address,
            status_id=building.status_id,
            created_at=building.created_at,
            updated_at=building.updated_at,
            owner_id=building.owner_id,
            owner=owner_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Ошибка загрузки деталей корпуса {building_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/floors/{floor_id}", response_model=FloorDetailResponse)
async def read_floor_detail(
    floor_id: int,
    db: Session = Depends(get_db)
) -> FloorDetailResponse:
    """Получить детальную информацию об этаже"""
    try:
        floor = db.get(Floor, floor_id)
        if not floor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Floor not found"
            )
        
        # ИСПРАВЛЕНО: используем first() вместо scalar_one()
        count_result = db.exec(
            select(func.count(Room.id)).where(Room.floor_id == floor_id) # type: ignore
        ).first()
        
        rooms_count = 0
        if count_result is not None:
            if isinstance(count_result, tuple) and len(count_result) > 0:
                rooms_count = int(count_result[0])
            else:
                rooms_count = int(count_result)

        log.info(f"Загружены детали этажа {floor_id}")
        
        return FloorDetailResponse(
            id=floor.id,  # type: ignore
            number=floor.number,
            building_id=floor.building_id,
            rooms_count=rooms_count,
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
        log.error(f"Ошибка загрузки деталей этажа {floor_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/rooms/{room_id}", response_model=RoomDetailResponse)
async def read_room_detail(
    room_id: int,
    include_tenant: bool = Query(False, description="Include tenant information"),
    db: Session = Depends(get_db)
) -> RoomDetailResponse:
    """
    Получить детальную информацию о помещении
    """
    try:
        room = db.get(Room, room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )

        log.info(f"Загружены детали помещения {room_id}")
        
        return RoomDetailResponse(
            id=room.id,  # type: ignore
            number=room.number,
            floor_id=room.floor_id,
            area=room.area,
            status_code=room.status_code,
            description=room.description,
            physical_type_id=room.physical_type_id,
            max_tenants=room.max_tenants,
            created_at=room.created_at,
            updated_at=room.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Ошибка загрузки деталей помещения {room_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )