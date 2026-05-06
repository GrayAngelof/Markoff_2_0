# backend/src/app/structure/schemas/detail.py
"""
Detail-схемы для физической иерархии (полные поля для панели деталей).
"""

from typing import Optional
from .base import StructureDetailBase


class ComplexDetailSchema(StructureDetailBase):
    """Комплекс (полная информация)."""
    name: str
    buildings_count: int
    address: Optional[str] = None
    owner_id: Optional[int] = None


class BuildingDetailSchema(StructureDetailBase):
    """Корпус (полная информация)."""
    name: str
    complex_id: int
    floors_count: int
    address: Optional[str] = None
    owner_id: Optional[int] = None


class FloorDetailSchema(StructureDetailBase):
    """Этаж (полная информация)."""
    number: int
    building_id: int
    rooms_count: int
    physical_type_id: Optional[int] = None
    plan_image_url: Optional[str] = None


class RoomDetailSchema(StructureDetailBase):
    """Помещение (полная информация)."""
    number: str
    floor_id: int
    area: Optional[float] = None
    physical_type_id: Optional[int] = None
    max_tenants: Optional[int] = None