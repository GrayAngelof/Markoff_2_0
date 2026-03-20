# Репозиторий для помещений
# Зависимости: .base, models, core

from typing import List, Optional
from core import NodeType
from models import Room
from .base import BaseRepository

class RoomRepository(BaseRepository[Room]):
    """Репозиторий для работы с помещениями"""
    
    def __init__(self, graph):
        super().__init__(graph, NodeType.ROOM)
    
    def get_by_floor(self, floor_id: int) -> List[Room]:
        """Возвращает все помещения этажа."""
        room_ids = self._graph.get_children(NodeType.FLOOR, floor_id)
        return [self.get(id) for id in room_ids if self.get(id)]
    
    def get_by_status(self, status_code: str) -> List[Room]:
        """Возвращает помещения по статусу."""
        all_rooms = self.get_all()
        return [r for r in all_rooms if r.status_code == status_code]
    
    def find_by_number(self, number_part: str) -> List[Room]:
        """Поиск по номеру помещения."""
        all_rooms = self.get_all()
        return [r for r in all_rooms if number_part in r.number]