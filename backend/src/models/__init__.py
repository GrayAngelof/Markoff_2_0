# backend/src/models/__init__.py
"""
Инициализатор пакета моделей.

Экспортирует модели из всех схем:
- physical: физическая структура (Complex, Building, Floor, Room, Zone)
- dictionary: справочные данные (BuildingStatus, RoomStatus)
"""

# ===== ИМПОРТЫ =====
from .dictionary import BuildingStatus, RoomStatus
from .physical import Building, Complex, Floor, Room, Zone


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Physical
    "Building",
    "Complex",
    "Floor",
    "Room",
    "Zone",
    # Dictionary
    "BuildingStatus",
    "RoomStatus",
]