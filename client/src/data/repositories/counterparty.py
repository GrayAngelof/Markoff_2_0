# client/src/data/repositories/counterparty.py
"""
Репозиторий для контрагентов.

ТОЛЬКО БАЗОВЫЕ ОПЕРАЦИИ ДОСТУПА:
- get() — получение по ID
- get_all() — все сущности
- get_ids() — все ID
- exists() — проверка существования
- add() — добавление/обновление
- remove() — удаление
- get_person_ids() — навигация по графу (получение ID детей)

Никакой бизнес-логики: фильтрация, поиск по ИНН, статус — только в сервисах!
"""
from typing import List
from src.core import NodeType, NotFoundError
from src.models import Counterparty
from .base import BaseRepository


class CounterpartyRepository(BaseRepository[Counterparty]):
    """
    Репозиторий для работы с контрагентами.
    
    Только базовые операции доступа к данным.
    """
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.COUNTERPARTY)
    
    # ===== Навигация по графу (это доступ, а не бизнес-логика) =====
    
    def get_person_ids(self, counterparty_id: int) -> List[int]:
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
    # get(id) -> Counterparty (или NotFoundError)
    # get_all() -> List[Counterparty]
    # get_ids() -> List[int]
    # exists(id) -> bool
    # add(entity) -> None
    # remove(id) -> None
    # is_valid(id) -> bool
    # invalidate(id) -> bool