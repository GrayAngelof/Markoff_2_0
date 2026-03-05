# backend/src/routers/physical.py
"""
Роутер для работы с physical данными
Обрабатывает запросы для всех уровней иерархии
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import List

from ..core.deps import get_db
from ..models.physical import Complex, Building, Floor, Room
from ..schemas.physical import (
    # Базовые схемы для дерева
    ComplexTreeResponse,
    BuildingTreeResponse,
    FloorTreeResponse,
    RoomTreeResponse,
    # Детальные схемы для правой панели
    ComplexDetailResponse,
    BuildingDetailResponse,
    FloorDetailResponse,
    RoomDetailResponse
)

router = APIRouter(prefix="/physical", tags=["physical"])

# ===== Эндпоинты для комплексов (дерево) =====
@router.get("/", response_model=List[ComplexTreeResponse])
async def read_complexes(
    db: Session = Depends(get_db)
) -> List[ComplexTreeResponse]:
    """Получить список всех комплексов для дерева"""
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
        
        complexes = []
        for row in result:
            complexes.append(ComplexTreeResponse(
                id=row.id,
                name=row.name,
                buildings_count=row.buildings_count
            ))
        
        return complexes
    except Exception as e:
        print(f"❌ Error in /physical/: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# ===== Эндпоинты для корпусов (дерево) =====
@router.get("/complexes/{complex_id}/buildings", response_model=List[BuildingTreeResponse])
async def read_buildings(
    complex_id: int,
    db: Session = Depends(get_db)
) -> List[BuildingTreeResponse]:
    """Получить список корпусов для конкретного комплекса"""
    try:
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
        
        result = db.exec(statement)
        
        buildings = []
        for row in result:
            buildings.append(BuildingTreeResponse(
                id=row.id,
                name=row.name,
                complex_id=row.complex_id,
                floors_count=row.floors_count
            ))
        
        return buildings
    except Exception as e:
        print(f"❌ Error in /complexes/{complex_id}/buildings: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# ===== Эндпоинты для этажей (дерево) =====
@router.get("/buildings/{building_id}/floors", response_model=List[FloorTreeResponse])
async def read_floors(
    building_id: int,
    db: Session = Depends(get_db)
) -> List[FloorTreeResponse]:
    """Получить список этажей для конкретного корпуса"""
    try:
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
            floors.append(FloorTreeResponse(
                id=row.id,
                number=row.number,
                building_id=row.building_id,
                rooms_count=row.rooms_count
            ))
        
        return floors
    except Exception as e:
        print(f"❌ Error in /buildings/{building_id}/floors: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# ===== Эндпоинты для помещений (дерево) =====
@router.get("/floors/{floor_id}/rooms", response_model=List[RoomTreeResponse])
async def read_rooms(
    floor_id: int,
    db: Session = Depends(get_db)
) -> List[RoomTreeResponse]:
    """Получить список помещений для конкретного этажа"""
    try:
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
            rooms.append(RoomTreeResponse(
                id=row.id,
                number=row.number,
                floor_id=row.floor_id,
                area=row.area,
                status_code=row.status_code
            ))
        
        return rooms
    except Exception as e:
        print(f"❌ Error in /floors/{floor_id}/rooms: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# ===== Детальные эндпоинты для правой панели =====

@router.get("/complexes/{complex_id}", response_model=ComplexDetailResponse)
async def read_complex_detail(
    complex_id: int,
    db: Session = Depends(get_db)
) -> ComplexDetailResponse:
    """Получить детальную информацию о комплексе"""
    try:
        print(f"🔍 GET /physical/complexes/{complex_id} - запрос деталей")
        
        complex = db.get(Complex, complex_id)
        if not complex:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complex not found"
            )
        
        # Подсчитываем количество корпусов
        buildings_count = db.exec(
            select(func.count(Building.id)).where(Building.complex_id == complex_id)
        ).one()
        
        return ComplexDetailResponse(
            id=complex.id,
            name=complex.name,
            buildings_count=buildings_count,
            description=complex.description,
            address=complex.address,
            owner_id=complex.owner_id,
            created_at=complex.created_at,
            updated_at=complex.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in /complexes/{complex_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/buildings/{building_id}", response_model=BuildingDetailResponse)
async def read_building_detail(
    building_id: int,
    db: Session = Depends(get_db)
) -> BuildingDetailResponse:
    """Получить детальную информацию о корпусе"""
    try:
        print(f"🔍 GET /physical/buildings/{building_id} - запрос деталей")
        
        building = db.get(Building, building_id)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Building not found"
            )
        
        # Подсчитываем количество этажей
        floors_count = db.exec(
            select(func.count(Floor.id)).where(Floor.building_id == building_id)
        ).one()
        
        return BuildingDetailResponse(
            id=building.id,
            name=building.name,
            complex_id=building.complex_id,
            floors_count=floors_count,
            description=building.description,
            address=building.address,
            status_id=building.status_id,
            created_at=building.created_at,
            updated_at=building.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in /buildings/{building_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/floors/{floor_id}", response_model=FloorDetailResponse)
async def read_floor_detail(
    floor_id: int,
    db: Session = Depends(get_db)
) -> FloorDetailResponse:
    """Получить детальную информацию об этаже"""
    try:
        print(f"🔍 GET /physical/floors/{floor_id} - запрос деталей")
        
        floor = db.get(Floor, floor_id)
        if not floor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Floor not found"
            )
        
        # Подсчитываем количество помещений
        rooms_count = db.exec(
            select(func.count(Room.id)).where(Room.floor_id == floor_id)
        ).one()
        
        return FloorDetailResponse(
            id=floor.id,
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
        print(f"❌ Error in /floors/{floor_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/rooms/{room_id}", response_model=RoomDetailResponse)
async def read_room_detail(
    room_id: int,
    db: Session = Depends(get_db)
) -> RoomDetailResponse:
    """
    Получить детальную информацию о помещении
    """
    try:
        print(f"🔍 GET /physical/rooms/{room_id} - запрос деталей")
        
        # Получаем помещение
        room = db.get(Room, room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )
        
        # Проверяем, что все необходимые поля есть
        print(f"📦 Данные из БД: id={room.id}, number={room.number}, floor_id={room.floor_id}")
        print(f"   area={room.area}, status_code={room.status_code}")
        print(f"   description={room.description}, physical_type_id={room.physical_type_id}")
        
        return RoomDetailResponse(
            id=room.id,
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
        print(f"❌ Error in /rooms/{room_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )