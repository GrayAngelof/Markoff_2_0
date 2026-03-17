# client/src/data/graph/validity_index.py
"""
Индекс валидности данных.
Отвечает только за пометку устаревших сущностей.
"""
from threading import RLock
from typing import Dict, Set, List

from src.data.entity_types import NodeType, COMPLEX, BUILDING, FLOOR, ROOM, COUNTERPARTY, RESPONSIBLE_PERSON
from src.data.graph.schema import get_child_type  # <-- ИСПРАВЛЕНО: импортируем функцию, а не класс

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
            COMPLEX: set(),
            BUILDING: set(),
            FLOOR: set(),
            ROOM: set(),
            COUNTERPARTY: set(),  # <-- ДОБАВЛЕНО
            RESPONSIBLE_PERSON: set(),  # <-- ДОБАВЛЕНО
        }
        
        log.debug("ValidityIndex инициализирован")
    
    def mark_valid(self, node_type: NodeType, entity_id: int) -> None:
        """
        Помечает сущность как валидную.
        """
        with self._lock:
            if node_type not in self._valid:
                log.warning(f"Неизвестный тип узла: {node_type}")
                return
            self._valid[node_type].add(entity_id)
            log.debug(f"VALID {node_type.value}#{entity_id}")
    
    def mark_invalid(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Помечает сущность как невалидную.
        Returns: True если статус изменился
        """
        with self._lock:
            if node_type not in self._valid:
                log.warning(f"Неизвестный тип узла: {node_type}")
                return False
            
            if entity_id in self._valid[node_type]:
                self._valid[node_type].remove(entity_id)
                log.debug(f"INVALID {node_type.value}#{entity_id}")
                return True
            return False
    
    def is_valid(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Проверяет, валидна ли сущность.
        """
        with self._lock:
            if node_type not in self._valid:
                return False
            return entity_id in self._valid.get(node_type, set())
    
    def invalidate_branch(self, node_type: NodeType, entity_id: int, 
                         get_children_fn) -> int:
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
            
            # Определяем тип детей
            child_type = get_child_type(node_type)
            
            if child_type and child_type in self._valid:
                for child_id in child_ids:
                    count += self.invalidate_branch(child_type, child_id, get_children_fn)
            
            return count
    
    def get_valid_ids(self, node_type: NodeType) -> List[int]:
        """
        Возвращает список валидных ID для указанного типа.
        """
        with self._lock:
            if node_type not in self._valid:
                return []
            return list(self._valid[node_type])
    
    def clear(self) -> None:
        """Очищает все индексы валидности."""
        with self._lock:
            for node_type in self._valid:
                self._valid[node_type].clear()
            log.debug("ValidityIndex очищен")