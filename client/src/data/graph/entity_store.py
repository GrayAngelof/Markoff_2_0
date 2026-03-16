# client/src/data/graph/entity_store.py
"""
Хранилище сущностей - только хранение объектов.
Никакой логики связей, только put/get/remove.
"""
from threading import RLock
from typing import Dict, Optional, Any, List
from datetime import datetime

from src.data.entity_types import NodeType
from src.data.graph.schema import NODETYPE_TO_MODEL
from utils.logger import get_logger

log = get_logger(__name__)


class EntityStore:
    """
    Хранилище сущностей.
    Отвечает только за сохранение и выдачу объектов по ID.
    """
    
    def __init__(self):
        self._lock = RLock()
        
        # Основное хранилище: тип узла -> {id: объект}
        self._entities: Dict[NodeType, Dict[int, Any]] = {
            NodeType.COMPLEX: {},
            NodeType.BUILDING: {},
            NodeType.FLOOR: {},
            NodeType.ROOM: {}
        }
        
        # Временные метки для каждого объекта
        self._timestamps: Dict[NodeType, Dict[int, datetime]] = {
            NodeType.COMPLEX: {},
            NodeType.BUILDING: {},
            NodeType.FLOOR: {},
            NodeType.ROOM: {}
        }
        
        log.debug("EntityStore инициализирован")
    
    def put(self, node_type: NodeType, entity_id: int, entity: Any) -> None:
        """
        Сохраняет сущность в хранилище.
        """
        with self._lock:
            self._entities[node_type][entity_id] = entity
            self._timestamps[node_type][entity_id] = datetime.now()
            log.debug(f"PUT {node_type.value}#{entity_id}")
    
    def get(self, node_type: NodeType, entity_id: int) -> Optional[Any]:
        """
        Получает сущность по типу и ID.
        """
        with self._lock:
            return self._entities.get(node_type, {}).get(entity_id)
    
    def get_all(self, node_type: NodeType) -> List[Any]:
        """
        Получает все сущности указанного типа.
        """
        with self._lock:
            return list(self._entities.get(node_type, {}).values())
    
    def get_all_ids(self, node_type: NodeType) -> List[int]:
        """
        Получает все ID сущностей указанного типа.
        """
        with self._lock:
            return list(self._entities.get(node_type, {}).keys())
    
    def remove(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Удаляет сущность из хранилища.
        """
        with self._lock:
            if entity_id in self._entities[node_type]:
                del self._entities[node_type][entity_id]
                if entity_id in self._timestamps[node_type]:
                    del self._timestamps[node_type][entity_id]
                log.debug(f"REMOVE {node_type.value}#{entity_id}")
                return True
            return False
    
    def has(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Проверяет наличие сущности.
        """
        with self._lock:
            return entity_id in self._entities.get(node_type, {})
    
    def get_timestamp(self, node_type: NodeType, entity_id: int) -> Optional[datetime]:
        """
        Возвращает временную метку последнего обновления.
        """
        with self._lock:
            return self._timestamps.get(node_type, {}).get(entity_id)
    
    def clear(self) -> None:
        """
        Полностью очищает хранилище.
        """
        with self._lock:
            for node_type in self._entities:
                self._entities[node_type].clear()
                self._timestamps[node_type].clear()
            log.debug("EntityStore очищен")
    
    def size(self) -> int:
        """
        Возвращает общее количество сущностей.
        """
        with self._lock:
            return sum(len(store) for store in self._entities.values())