# backend/src/schemas/__init__.py
"""
Pydantic схемы для API.

Экспортирует схемы из всех модулей:
- physical: схемы физической структуры (Tree и Detail)
- dictionary: схемы справочных данных
"""

# ===== ИМПОРТЫ =====
from .dictionary import BuildingStatusResponse, RoomStatusResponse
from .physical import (
    BuildingDetailResponse,
    BuildingTreeResponse,
    ComplexDetailResponse,
    ComplexTreeResponse,
    FloorDetailResponse,
    FloorTreeResponse,
    RoomDetailResponse,
    RoomTreeResponse,
)


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Physical (Tree)
    "BuildingTreeResponse",
    "ComplexTreeResponse",
    "FloorTreeResponse",
    "RoomTreeResponse",
    # Physical (Detail)
    "BuildingDetailResponse",
    "ComplexDetailResponse",
    "FloorDetailResponse",
    "RoomDetailResponse",
    # Dictionary
    "BuildingStatusResponse",
    "RoomStatusResponse",
]