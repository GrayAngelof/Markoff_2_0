# backend/src/app/structure/schemas/__init__.py
"""
Pydantic схемы для физической иерархии (structure).
"""

from .tree import (
    ComplexTreeSchema,
    BuildingTreeSchema,
    FloorTreeSchema,
    RoomTreeSchema
)
from .detail import (
    ComplexDetailSchema, 
    BuildingDetailSchema, 
    FloorDetailSchema, 
    RoomDetailSchema
)

__all__ = [
    # Tree
    "ComplexTreeSchema",
    "BuildingTreeSchema",
    "FloorTreeSchema",
    "RoomTreeSchema",
    # Detail
    "ComplexDetailSchema",
    "BuildingDetailSchema",
    "FloorDetailSchema",
    "RoomDetailSchema",
]