# backend/src/models/dictionary/__init__.py
"""
Инициализатор пакета моделей схемы dictionary
"""
from .building_status import BuildingStatus
from .room_status import RoomStatus

__all__ = [
    "BuildingStatus",
    "RoomStatus",
]