# client/src/data/repositories/complex.py
"""
Репозиторий для комплексов.

ТОЛЬКО БАЗОВЫЕ ОПЕРАЦИИ ДОСТУПА:
- get() — получение по ID
- get_all() — все сущности
- get_ids() — все ID
- exists() — проверка существования
- add() — добавление/обновление
- remove() — удаление
- get_building_ids() — навигация по графу (получение ID детей)

Никакой бизнес-логики: фильтрация по владельцу, поиск по имени — только в сервисах!
"""
from typing import List
from src.core import NodeType, NotFoundError
from src.models import Complex
from .base import BaseRepository


class ComplexRepository(BaseRepository[Complex]):
    """
    Репозиторий для работы с комплексами.
    
    Только базовые операции доступа к данным.
    """
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.COMPLEX)
    
    # ===== Навигация по графу (это доступ, а не бизнес-логика) =====
    
    def get_building_ids(self, complex_id: int) -> List[int]:
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
    # get(id) -> Complex (или NotFoundError)
    # get_all() -> List[Complex]
    # get_ids() -> List[int]
    # exists(id) -> bool
    # add(entity) -> None
    # remove(id) -> None
    # is_valid(id) -> bool
    # invalidate(id) -> bool