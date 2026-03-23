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
- get_by_complex() — навигация по графу (получение ID родителей?)

Никакой бизнес-логики: фильтрация по владельцу — только в сервисах!
"""
from typing import List
from core import NodeType, NotFoundError
from models import Building
from .base import BaseRepository


class BuildingRepository(BaseRepository[Building]):
    """
    Репозиторий для работы с корпусами.
    
    Только базовые операции доступа к данным.
    """
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.BUILDING)
    
    # ===== Навигация по графу (это доступ, а не бизнес-логика) =====
    
    def get_floor_ids(self, building_id: int) -> List[int]:
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
    
    def get_by_complex(self, complex_id: int) -> List[int]:
        """
        Возвращает ID всех корпусов комплекса.
        
        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            List[int]: Список ID корпусов
        """
        return self._graph.get_children(NodeType.COMPLEX, complex_id)
    
    # ===== Базовые операции (наследуются от BaseRepository) =====
    # get(id) -> Building (или NotFoundError)
    # get_all() -> List[Building]
    # get_ids() -> List[int]
    # exists(id) -> bool
    # add(entity) -> None
    # remove(id) -> None
    # is_valid(id) -> bool
    # invalidate(id) -> bool