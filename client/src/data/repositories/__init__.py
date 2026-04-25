# client/src/data/repositories/__init__.py
"""
Публичное API репозиториев.

Репозитории обеспечивают высокоуровневый доступ к данным в EntityGraph:
- Получение сущностей по ID
- Получение детей (корпуса комплекса, этажи корпуса, помещения этажа)
- Поиск и фильтрация

ЕДИНСТВЕННЫЙ способ импорта репозиториев:
    from src.data.repositories import ComplexRepository, BuildingRepository

ПРИМЕЧАНИЕ:
    BaseRepository — внутренняя деталь реализации, не экспортируется.
    Для создания кастомных репозиториев наследуйтесь от BaseRepository
    напрямую из src.data.repositories.base, но это требуется только
    при добавлении новых типов сущностей.
"""

# ===== ИМПОРТЫ =====
from .complex import ComplexRepository
from .building import BuildingRepository
from .floor import FloorRepository
from .room import RoomRepository


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Репозиторий для комплексов (верхний уровень иерархии)
    "ComplexRepository",
    
    # Репозиторий для корпусов (дети комплекса)
    "BuildingRepository",
    
    # Репозиторий для этажей (дети корпуса)
    "FloorRepository",
    
    # Репозиторий для помещений (дети этажа)
    "RoomRepository",
]