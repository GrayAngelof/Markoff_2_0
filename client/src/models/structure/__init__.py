# client/src/models/structure/__init__.py
"""
DTO для физической иерархии (structure layer).
"""

from .complex import ComplexTreeDTO, ComplexDetailDTO
from .building import BuildingTreeDTO, BuildingDetailDTO
from .floor import FloorTreeDTO, FloorDetailDTO
from .room import RoomTreeDTO, RoomDetailDTO

__all__ = [
    "ComplexTreeDTO",
    "ComplexDetailDTO",
    "BuildingTreeDTO",
    "BuildingDetailDTO",
    "FloorTreeDTO",
    "FloorDetailDTO",
    "RoomTreeDTO",
    "RoomDetailDTO",
]