# backend/src/schemas/physical.py
"""
Pydantic схемы для ответов API
Содержат как минимальные поля для дерева, так и детальные для просмотра
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


# ===== Базовые схемы (для дерева) =====

class ComplexTreeResponse(BaseModel):
    """Минимальная информация о комплексе для дерева"""
    id: int
    name: str
    buildings_count: int

    model_config = ConfigDict(from_attributes=True)


class BuildingTreeResponse(BaseModel):
    """Минимальная информация о корпусе для дерева"""
    id: int
    name: str
    complex_id: int
    floors_count: int

    model_config = ConfigDict(from_attributes=True)


class FloorTreeResponse(BaseModel):
    """Минимальная информация об этаже для дерева"""
    id: int
    number: int
    building_id: int
    rooms_count: int

    model_config = ConfigDict(from_attributes=True)


class RoomTreeResponse(BaseModel):
    """Минимальная информация о помещении для дерева"""
    id: int
    number: str
    floor_id: int
    area: Optional[float] = None
    status_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ===== Детальные схемы (для правой панели) =====

class ComplexDetailResponse(BaseModel):
    """Детальная информация о комплексе"""
    id: int
    name: str
    buildings_count: int
    description: Optional[str] = None
    address: Optional[str] = None
    owner_id: Optional[int] = None
    status_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BuildingDetailResponse(BaseModel):
    """Детальная информация о корпусе"""
    id: int
    name: str
    complex_id: int
    floors_count: int
    description: Optional[str] = None
    address: Optional[str] = None
    owner_id: Optional[int] = None
    status_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FloorDetailResponse(BaseModel):
    """Детальная информация об этаже"""
    id: int
    number: int
    building_id: int
    rooms_count: int
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    status_id: Optional[int] = None
    plan_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomDetailResponse(BaseModel):
    """Детальная информация о помещении"""
    id: int
    number: str
    floor_id: int
    area: Optional[float] = None
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    status_id: Optional[int] = None
    max_tenants: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)