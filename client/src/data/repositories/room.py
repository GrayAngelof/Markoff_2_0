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
Работает с TreeDTO и DetailDTO.
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional, Union, cast

from src.core import NodeType
from src.models import RoomTreeDTO, RoomDetailDTO
from src.data.repositories.base import BaseRepository


# ===== ТИПЫ =====
# Репозиторий может хранить как Tree, так и Detail DTO
RoomDTO = Union[RoomTreeDTO, RoomDetailDTO]


# ===== КЛАСС =====
class RoomRepository(BaseRepository[RoomDTO]):
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

    # ---- УДОБНЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С TREE/DETAIL ----
    def get_tree(self, room_id: int) -> Optional[RoomTreeDTO]:
        """
        Возвращает TreeDTO помещения (минимальные данные).

        Returns:
            RoomTreeDTO или None, если не найден
        """
        entity = self.get(room_id)
        if entity and not entity.IS_DETAIL:
            return cast(RoomTreeDTO, entity)
        return None

    def get_detail(self, room_id: int) -> Optional[RoomDetailDTO]:
        """
        Возвращает DetailDTO помещения (полные данные).

        Returns:
            RoomDetailDTO или None, если не найден или есть только TreeDTO
        """
        entity = self.get(room_id)
        if entity and entity.IS_DETAIL:
            return cast(RoomDetailDTO, entity)
        return None

    def has_detail(self, room_id: int) -> bool:
        """Проверяет, загружены ли полные данные помещения."""
        entity = self.get(room_id)
        return entity is not None and entity.IS_DETAIL