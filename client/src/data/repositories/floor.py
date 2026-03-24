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
- get_by_building() — навигация по графу (получение ID родителей?)

Никакой бизнес-логики: сортировка, фильтрация — только в сервисах!
"""
from typing import List
from src.core import NodeType, NotFoundError
from src.models import Floor
from .base import BaseRepository


class FloorRepository(BaseRepository[Floor]):
    """
    Репозиторий для работы с этажами.
    
    Только базовые операции доступа к данным.
    """
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.FLOOR)
    
    # ===== Навигация по графу (это доступ, а не бизнес-логика) =====
    
    def get_room_ids(self, floor_id: int) -> List[int]:
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
    
    def get_by_building(self, building_id: int) -> List[int]:
        """
        Возвращает ID всех этажей корпуса.
        
        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        
        Args:
            building_id: ID корпуса
            
        Returns:
            List[int]: Список ID этажей
        """
        return self._graph.get_children(NodeType.BUILDING, building_id)
    
    # ===== Базовые операции (наследуются от BaseRepository) =====
    # get(id) -> Floor (или NotFoundError)
    # get_all() -> List[Floor]
    # get_ids() -> List[int]
    # exists(id) -> bool
    # add(entity) -> None
    # remove(id) -> None
    # is_valid(id) -> bool
    # invalidate(id) -> bool