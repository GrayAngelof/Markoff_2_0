# Репозиторий для ответственных лиц
# Зависимости: .base, models, core

from typing import List, Optional
from core import NodeType
from models import ResponsiblePerson
from .base import BaseRepository

class ResponsiblePersonRepository(BaseRepository[ResponsiblePerson]):
    """Репозиторий для работы с ответственными лицами"""
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.RESPONSIBLE_PERSON)
    
    def get_by_counterparty(self, counterparty_id: int) -> List[ResponsiblePerson]:
        """Возвращает всех ответственных лиц контрагента."""
        person_ids = self._graph.get_children(NodeType.COUNTERPARTY, counterparty_id)
        return [self.get(id) for id in person_ids if self.get(id)]
    
    def get_active_by_counterparty(self, counterparty_id: int) -> List[ResponsiblePerson]:
        """Возвращает только активных."""
        all_persons = self.get_by_counterparty(counterparty_id)
        return [p for p in all_persons if p.is_active]
    
    def get_by_category(self, category: str) -> List[ResponsiblePerson]:
        """Поиск по категории контакта."""
        all_persons = self.get_all()
        result = []
        for p in all_persons:
            if p.contact_categories and category in p.contact_categories:
                result.append(p)
        return result