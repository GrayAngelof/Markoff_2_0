# backend/src/models/physical/__init__.py
"""
Инициализатор пакета моделей схемы physical
Экспортирует все модели для удобного импорта
"""
from .complex import Complex
from .building import Building
from .floor import Floor
from .room import Room
from .zone import Zone

__all__ = ["Complex", "Building", "Floor", "Room", "Zone"]