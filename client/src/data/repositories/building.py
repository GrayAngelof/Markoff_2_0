# client/src/data/repositories/building.py
"""
Репозиторий для корпусов.

ТОЛЬКО БАЗОВЫЕ ОПЕРАЦИИ ДОСТУПА:
- get() — получение по ID
- get_all() — все сущности
- get_ids() — все ID
- exists() — проверка существования
- add() — добавление/обновление
- remove() — удаление
- get_floor_ids() — навигация по графу (получение ID детей)
- get_by_complex() — навигация по графу (получение ID корпусов комплекса)

Никакой бизнес-логики: фильтрация по владельцу — только в сервисах!
"""

# ===== ИМПОРТЫ =====
from typing import List

from src.core import NodeType
from src.models import Building
from .base import BaseRepository


# ===== КЛАСС =====
class BuildingRepository(BaseRepository[Building]):
    """Репозиторий для работы с корпусами."""

    def __init__(self, graph) -> None:
        super().__init__(graph, NodeType.BUILDING)

    # ---- НАВИГАЦИЯ ПО ГРАФУ ----
    def get_floor_ids(self, building_id: int) -> List[int]:
        """
        Возвращает ID всех этажей корпуса.

        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        """
        return self._graph.get_children(NodeType.BUILDING, building_id)

    def get_by_complex(self, complex_id: int) -> List[int]:
        """
        Возвращает ID всех корпусов комплекса.

        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        """
        return self._graph.get_children(NodeType.COMPLEX, complex_id)