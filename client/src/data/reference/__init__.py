# client/src/data/reference/__init__.py
"""
Приватный пакет реестров справочников.

Содержит базовый класс и конкретные реализации реестров для:
- Статусов зданий (BuildingStatusRegistry)
- Статусов помещений (RoomStatusRegistry)

ВНИМАНИЕ: Это ПРИВАТНЫЙ пакет.
Не импортировать напрямую извне.
Используйте ReferenceStore (src.data.reference_store) как фасад.
"""

from .base import BaseRegistry
from .building_status_registry import BuildingStatusRegistry
from .room_status_registry import RoomStatusRegistry

__all__ = [
    "BaseRegistry",
    "BuildingStatusRegistry",
    "RoomStatusRegistry",
]