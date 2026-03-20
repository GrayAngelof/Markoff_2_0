# Репозиторий для этажей
# Зависимости: .base, models, core

from typing import List, Optional
from core import NodeType
from models import Floor
from .base import BaseRepository

class FloorRepository(BaseRepository[Floor]):
    """Репозиторий для работы с этажами"""
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.FLOOR)
    
    def get_room_ids(self, floor_id: int) -> List[int]:
        """Возвращает ID всех помещений этажа."""
        return self._graph.get_children(NodeType.FLOOR, floor_id)
    
    def get_by_building(self, building_id: int) -> List[Floor]:
        """Возвращает все этажи корпуса."""
        floor_ids = self._graph.get_children(NodeType.BUILDING, building_id)
        return [self.get(id) for id in floor_ids if self.get(id)]
    
    def get_sorted_by_number(self, building_id: int) -> List[Floor]:
        """Возвращает этажи, отсортированные по номеру."""
        floors = self.get_by_building(building_id)
        return sorted(floors, key=lambda f: f.number)