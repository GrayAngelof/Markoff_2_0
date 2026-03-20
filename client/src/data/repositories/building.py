# Репозиторий для корпусов
# Зависимости: .base, models, core

from typing import List, Optional
from core import NodeType
from models import Building
from .base import BaseRepository

class BuildingRepository(BaseRepository[Building]):
    """Репозиторий для работы с корпусами"""
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.BUILDING)
    
    def get_floor_ids(self, building_id: int) -> List[int]:
        """Возвращает ID всех этажей корпуса."""
        return self._graph.get_children(NodeType.BUILDING, building_id)
    
    def get_by_complex(self, complex_id: int) -> List[Building]:
        """Возвращает все корпуса комплекса."""
        building_ids = self._graph.get_children(NodeType.COMPLEX, complex_id)
        return [self.get(id) for id in building_ids if self.get(id)]
    
    def get_by_owner(self, owner_id: int) -> List[Building]:
        """Возвращает корпуса по владельцу."""
        all_buildings = self.get_all()
        return [b for b in all_buildings if b.owner_id == owner_id]