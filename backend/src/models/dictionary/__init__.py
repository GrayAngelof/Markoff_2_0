# backend/src/models/dictionary/__init__.py
"""
Инициализатор пакета моделей схемы dictionary.

Экспортирует модели справочных данных:
- BuildingStatus — статусы зданий
- RoomStatus — статусы помещений
"""

# ===== ИМПОРТЫ =====
from .building_status import BuildingStatus
from .room_status import RoomStatus


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    "BuildingStatus",
    "RoomStatus",
]