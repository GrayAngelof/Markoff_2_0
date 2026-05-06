# backend/src/app/structure/schemas/tree.py
"""
Tree-схемы для физической иерархии (минимальные поля для дерева).
"""

from typing import Optional
from .base import StructureTreeBase


class ComplexTreeSchema(StructureTreeBase):
    """Комплекс (минимально для дерева)."""
    name: str
    buildings_count: int


class BuildingTreeSchema(StructureTreeBase):
    """Корпус (минимально для дерева)."""
    name: str
    complex_id: int
    floors_count: int


class FloorTreeSchema(StructureTreeBase):
    """Этаж (минимально для дерева)."""
    number: int
    building_id: int
    rooms_count: int


class RoomTreeSchema(StructureTreeBase):
    """Помещение (минимально для дерева)."""
    number: str
    floor_id: int
    area: Optional[float] = None