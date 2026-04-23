# client/src/data/__init__.py
"""
Публичное API Data слоя.

Экспортирует:
- EntityGraph (фасад графа) — для низкоуровневого доступа
- Репозитории — для высокоуровневого доступа к данным
- Статистику

Внутренности (graph/*) не доступны напрямую.
"""

from .entity_graph import EntityGraph, EntityGraphStats
from .repositories import (
    BaseRepository,
    ComplexRepository,
    BuildingRepository,
    FloorRepository,
    RoomRepository,
)

__all__ = [
    # Фасад графа
    'EntityGraph',
    'EntityGraphStats',
    
    # Репозитории
    'BaseRepository',
    'ComplexRepository',
    'BuildingRepository',
    'FloorRepository',
    'RoomRepository',
]