# client/src/data/graph/validity_index.py
"""
Индекс валидности данных.
Отвечает только за пометку устаревших сущностей.
"""
from threading import RLock
from typing import Dict, Set, Callable, List

from src.data.entity_types import NodeType
from src.data.graph.schema import GraphSchema, get_child_type
from utils.logger import get_logger

log = get_logger(__name__)


class ValidityIndex:
    """
    Индекс валидности данных.
    
    Позволяет помечать сущности как устаревшие (требуют перезагрузки)
    и проверять их актуальность.
    """
    
    def __init__(self):
        self._lock = RLock()
        
        # Множества валидных ID для каждого типа
        self._valid: Dict[NodeType, Set[int]] = {
            node_type: set()
            for node_type in GraphSchema.HIERARCHY_ORDER
        }
        
        log.debug("ValidityIndex инициализирован")
    
    def mark_valid(self, node_type: NodeType, entity_id: int) -> None:
        """
        Помечает сущность как валидную.
        """
        with self._lock:
            self._valid[node_type].add(entity_id)
            log.debug(f"VALID {node_type}#{entity_id}")
    
    def mark_invalid(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Помечает сущность как невалидную.
        Returns: True если статус изменился
        """
        with self._lock:
            if entity_id in self._valid[node_type]:
                self._valid[node_type].remove(entity_id)
                log.debug(f"INVALID {node_type}#{entity_id}")
                return True
            return False
    
    def is_valid(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Проверяет, валидна ли сущность.
        """
        with self._lock:
            return entity_id in self._valid.get(node_type, set())
    
    def invalidate_branch(self, node_type: NodeType, entity_id: int, 
                         get_children_fn: Callable[[NodeType, int], List[int]]) -> int:
        """
        Рекурсивно инвалидирует ветку.
        get_children_fn - функция для получения детей (из RelationIndex)
        """
        with self._lock:
            count = 0
            if self.mark_invalid(node_type, entity_id):
                count += 1
            
            # Рекурсивно инвалидируем детей
            child_ids = get_children_fn(node_type, entity_id)
            child_type = get_child_type(node_type)
            
            if child_type is not None:
                for child_id in child_ids:
                    count += self.invalidate_branch(child_type, child_id, get_children_fn)
            
            return count
    
    def clear(self) -> None:
        """
        Очищает все индексы валидности.
        """
        with self._lock:
            for node_type in self._valid:
                self._valid[node_type].clear()
            log.debug("ValidityIndex очищен")