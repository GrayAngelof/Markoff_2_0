# client/src/data/repositories/room.py
"""
Репозиторий для помещений.

ТОЛЬКО БАЗОВЫЕ ОПЕРАЦИИ ДОСТУПА:
- get() — получение по ID
- get_all() — все сущности
- get_ids() — все ID
- exists() — проверка существования
- add() — добавление/обновление
- remove() — удаление
- get_by_floor() — навигация по графу (получение ID детей)

Никакой бизнес-логики: фильтрация по статусу, поиск по номеру — только в сервисах!
"""

# ===== ИМПОРТЫ =====
from typing import List

from src.core import NodeType, NotFoundError
from src.models import Room
from .base import BaseRepository


# ===== КЛАСС =====
class RoomRepository(BaseRepository[Room]):
    """Репозиторий для работы с помещениями."""

    def __init__(self, graph) -> None:
        super().__init__(graph, NodeType.ROOM)

    # ---- НАВИГАЦИЯ ПО ГРАФУ ----
    def get_by_floor(self, floor_id: int) -> List[int]:
        """
        Возвращает ID всех помещений этажа.

        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        """
        return self._graph.get_children(NodeType.FLOOR, floor_id)