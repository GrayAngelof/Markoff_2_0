# Репозиторий для комплексов
# Зависимости: .base, models, core

from typing import List, Optional
from core import NodeType
from models import Complex
from .base import BaseRepository

class ComplexRepository(BaseRepository[Complex]):
    """Репозиторий для работы с комплексами"""
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.COMPLEX)
    
    def get_building_ids(self, complex_id: int) -> List[int]:
        """Возвращает ID всех корпусов комплекса."""
        return self._graph.get_children(NodeType.COMPLEX, complex_id)
    
    def get_by_owner(self, owner_id: int) -> List[Complex]:
        """Возвращает комплексы по владельцу."""
        all_complexes = self.get_all()
        return [c for c in all_complexes if c.owner_id == owner_id]
    
    def find_by_name(self, name_part: str) -> List[Complex]:
        """Поиск комплексов по части названия."""
        all_complexes = self.get_all()
        return [c for c in all_complexes if name_part.lower() in c.name.lower()]