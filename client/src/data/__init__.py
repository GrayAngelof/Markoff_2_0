# client/src/data/__init__.py
"""
Публичное API Data слоя.

Data слой отвечает за хранение, кэширование и доступ к данным:
- EntityGraph — графовое хранилище сущностей с отслеживанием связей
- Репозитории — высокоуровневый доступ к данным (CRUD + навигация по дереву)
- ReferenceStore — read-only справочники (статусы, типы)

ЕДИНСТВЕННЫЙ способ импорта из data слоя:
    from src.data import EntityGraph, ComplexRepository, ReferenceStore

ПРИМЕЧАНИЕ:
    - BaseRepository — внутренняя деталь, не экспортируется
    - graph/* — приватный пакет, не импортировать напрямую
    - reference/ — приватный пакет, используйте ReferenceStore как фасад
"""

# ===== ИМПОРТЫ =====
from .entity_graph import EntityGraph, EntityGraphStats
from .reference_store import ReferenceStore
from .repositories import (
    BuildingRepository,
    ComplexRepository,
    FloorRepository,
    RoomRepository,
)


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Фасад графа (низкоуровневое хранилище сущностей)
    "EntityGraph",
    
    # Статистика состояния графа
    "EntityGraphStats",
    
    # Репозитории (высокоуровневый доступ к данным)
    "BuildingRepository",   # Корпуса
    "ComplexRepository",    # Комплексы (корень иерархии)
    "FloorRepository",      # Этажи
    "RoomRepository",       # Помещения
    
    # Справочные данные (read-only)
    "ReferenceStore",
]