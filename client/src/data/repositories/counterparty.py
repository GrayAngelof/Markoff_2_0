# Репозиторий для контрагентов
# Зависимости: .base, models, core

from typing import List, Optional
from core import NodeType
from models import Counterparty
from .base import BaseRepository

class CounterpartyRepository(BaseRepository[Counterparty]):
    """Репозиторий для работы с контрагентами"""
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.COUNTERPARTY)
    
    def get_person_ids(self, counterparty_id: int) -> List[int]:
        """Возвращает ID всех ответственных лиц."""
        return self._graph.get_children(NodeType.COUNTERPARTY, counterparty_id)
    
    def get_by_tax_id(self, tax_id: str) -> Optional[Counterparty]:
        """Поиск по ИНН."""
        all_counterparties = self.get_all()
        for c in all_counterparties:
            if c.tax_id == tax_id:
                return c
        return None
    
    def get_active(self) -> List[Counterparty]:
        """Возвращает только активных контрагентов."""
        all_c = self.get_all()
        return [c for c in all_c if c.status_code == 'active']