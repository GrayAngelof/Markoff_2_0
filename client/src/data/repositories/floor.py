# client/src/data/repositories/floor.py
"""
Репозиторий для этажей.

ТОЛЬКО БАЗОВЫЕ ОПЕРАЦИИ ДОСТУПА:
- get() — получение по ID
- get_all() — все сущности
- get_ids() — все ID
- exists() — проверка существования
- add() — добавление/обновление
- remove() — удаление
- get_room_ids() — навигация по графу (получение ID детей)
- get_by_building() — навигация по графу (получение ID этажей корпуса)

Никакой бизнес-логики: сортировка, фильтрация — только в сервисах!
Работает с TreeDTO и DetailDTO.
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional, Union, cast

from src.core.types import NodeType
from src.models import FloorTreeDTO, FloorDetailDTO
from .base import BaseRepository


# ===== ТИПЫ =====
# Репозиторий может хранить как Tree, так и Detail DTO
FloorDTO = Union[FloorTreeDTO, FloorDetailDTO]


# ===== КЛАСС =====
class FloorRepository(BaseRepository[FloorDTO]):
    """Репозиторий для работы с этажами."""

    def __init__(self, graph) -> None:
        super().__init__(graph, NodeType.FLOOR)

    # ---- НАВИГАЦИЯ ПО ГРАФУ ----
    def get_room_ids(self, floor_id: int) -> List[int]:
        """
        Возвращает ID всех помещений этажа.

        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        """
        return self._graph.get_children(NodeType.FLOOR, floor_id)

    def get_by_building(self, building_id: int) -> List[int]:
        """
        Возвращает ID всех этажей корпуса.

        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        """
        return self._graph.get_children(NodeType.BUILDING, building_id)

    # ---- УДОБНЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С TREE/DETAIL ----
    def get_tree(self, floor_id: int) -> Optional[FloorTreeDTO]:
        """
        Возвращает TreeDTO этажа (минимальные данные).

        Returns:
            FloorTreeDTO или None, если не найден
        """
        entity = self.get(floor_id)
        if entity and not entity.IS_DETAIL:
            return cast(FloorTreeDTO, entity)
        return None

    def get_detail(self, floor_id: int) -> Optional[FloorDetailDTO]:
        """
        Возвращает DetailDTO этажа (полные данные).

        Returns:
            FloorDetailDTO или None, если не найден или есть только TreeDTO
        """
        entity = self.get(floor_id)
        if entity and entity.IS_DETAIL:
            return cast(FloorDetailDTO, entity)
        return None

    def has_detail(self, floor_id: int) -> bool:
        """Проверяет, загружены ли полные данные этажа."""
        entity = self.get(floor_id)
        return entity is not None and entity.IS_DETAIL