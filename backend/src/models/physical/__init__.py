# backend/src/models/physical/__init__.py
"""
Инициализатор пакета моделей схемы physical.

Экспортирует модели физической структуры:
- Complex — комплекс зданий
- Building — здание/корпус
- Floor — этаж
- Room — помещение
- Zone — зона
"""

# ===== ИМПОРТЫ =====
from .building import Building
from .complex import Complex
from .floor import Floor
from .room import Room
from .zone import Zone


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    "Building",
    "Complex",
    "Floor",
    "Room",
    "Zone",
]