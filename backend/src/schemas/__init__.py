# backend/src/schemas/__init__.py
"""
Pydantic схемы для API
"""
from .physical import (
    ComplexTreeResponse,
    BuildingTreeResponse,
    FloorTreeResponse,
    RoomTreeResponse,
    ComplexDetailResponse,
    BuildingDetailResponse,
    FloorDetailResponse,
    RoomDetailResponse
)
from .dictionary import BuildingStatusResponse, RoomStatusResponse


__all__ = [
    # Physical
    "ComplexTreeResponse",
    "BuildingTreeResponse",
    "FloorTreeResponse",
    "RoomTreeResponse",
    "ComplexDetailResponse",
    "BuildingDetailResponse",
    "FloorDetailResponse",
    "RoomDetailResponse",
    
    # Dictionary
    "BuildingStatusResponse",
    "RoomStatusResponse",
]