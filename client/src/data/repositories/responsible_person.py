# client/src/data/repositories/responsible_person.py
"""
Репозиторий для ответственных лиц.

ТОЛЬКО БАЗОВЫЕ ОПЕРАЦИИ ДОСТУПА:
- get() — получение по ID
- get_all() — все сущности
- get_ids() — все ID
- exists() — проверка существования
- add() — добавление/обновление
- remove() — удаление
- get_by_counterparty() — навигация по графу (получение ID детей)

Никакой бизнес-логики: фильтрация, сортировка, агрегация — только в сервисах!
"""
from typing import List
from core import NodeType, NotFoundError
from models import ResponsiblePerson
from .base import BaseRepository


class ResponsiblePersonRepository(BaseRepository[ResponsiblePerson]):
    """
    Репозиторий для работы с ответственными лицами.
    
    Только базовые операции доступа к данным.
    """
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.RESPONSIBLE_PERSON)
    
    # ===== Навигация по графу (это доступ, а не бизнес-логика) =====
    
    def get_by_counterparty(self, counterparty_id: int) -> List[int]:
        """
        Возвращает ID всех ответственных лиц контрагента.
        
        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            List[int]: Список ID ответственных лиц
        """
        return self._graph.get_children(NodeType.COUNTERPARTY, counterparty_id)
    
    # ===== Базовые операции (наследуются от BaseRepository) =====
    # get(id) -> ResponsiblePerson (или NotFoundError)
    # get_all() -> List[ResponsiblePerson]
    # get_ids() -> List[int]
    # exists(id) -> bool
    # add(entity) -> None
    # remove(id) -> None
    # is_valid(id) -> bool
    # invalidate(id) -> bool