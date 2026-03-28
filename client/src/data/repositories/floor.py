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
"""

# ===== ИМПОРТЫ =====
from typing import List

from src.core import NodeType
from src.models import Floor
from .base import BaseRepository


# ===== КЛАСС =====
class FloorRepository(BaseRepository[Floor]):
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