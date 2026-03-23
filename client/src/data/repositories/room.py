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
from typing import List
from core import NodeType, NotFoundError
from models import Room
from .base import BaseRepository


class RoomRepository(BaseRepository[Room]):
    """
    Репозиторий для работы с помещениями.
    
    Только базовые операции доступа к данным.
    """
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.ROOM)
    
    # ===== Навигация по графу (это доступ, а не бизнес-логика) =====
    
    def get_by_floor(self, floor_id: int) -> List[int]:
        """
        Возвращает ID всех помещений этажа.
        
        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        
        Args:
            floor_id: ID этажа
            
        Returns:
            List[int]: Список ID помещений
        """
        return self._graph.get_children(NodeType.FLOOR, floor_id)
    
    # ===== Базовые операции (наследуются от BaseRepository) =====
    # get(id) -> Room (или NotFoundError)
    # get_all() -> List[Room]
    # get_ids() -> List[int]
    # exists(id) -> bool
    # add(entity) -> None
    # remove(id) -> None
    # is_valid(id) -> bool
    # invalidate(id) -> bool