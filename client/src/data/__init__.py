# client/src/data/__init__.py
"""
Публичное API Data слоя.

Экспортирует:
- EntityGraph (фасад графа) — для низкоуровневого доступа
- Репозитории — для высокоуровневого доступа к данным
- ReferenceStore — справочные данные (статусы, типы и т.д.)
- Статистику

Внутренности (graph/*) не доступны напрямую.
"""

# ===== ИМПОРТЫ =====
from .entity_graph import EntityGraph, EntityGraphStats
from .reference_store import ReferenceStore
from .repositories import (
    BaseRepository,
    BuildingRepository,
    ComplexRepository,
    FloorRepository,
    RoomRepository,
)


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Фасад графа
    "EntityGraph",
    "EntityGraphStats",
    # Репозитории
    "BaseRepository",
    "BuildingRepository",
    "ComplexRepository",
    "FloorRepository",
    "RoomRepository",
    # Справочные данные
    "ReferenceStore",
]