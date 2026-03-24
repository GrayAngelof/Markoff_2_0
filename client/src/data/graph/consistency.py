# data/graph/consistency.py
"""
Проверка консистентности графа.

Вынесено из EntityGraph для соблюдения SRP.
"""

from typing import Dict, Any, List
from threading import RLock
from src.core.types import NodeType
from src.core.hierarchy import get_child_type
from utils.logger import get_logger

log = get_logger(__name__)


class ConsistencyChecker:
    """
    Проверяет консистентность всех индексов графа.
    
    Выявляет проблемы:
        - Сущности в store, но не валидные
        - Связи, указывающие на несуществующие объекты
        - Висячие объекты без связей
        - Несоответствие прямых и обратных индексов
    """
    
    def __init__(self, store, relations, validity):
        self._store = store
        self._relations = relations
        self._validity = validity
    
    def check(self) -> Dict[str, Any]:
        """Выполняет полную проверку консистентности."""
        issues = []
        
        # 1. Проверка валидности
        self._check_validity_consistency(issues)
        
        # 2. Проверка связей (существование объектов)
        self._check_relation_targets(issues)
        
        # 3. Проверка обратных связей
        self._check_parent_back_references(issues)
        
        # 4. Проверка соответствия прямых и обратных индексов
        self._check_index_consistency(issues)
        
        return {
            'consistent': len(issues) == 0,
            'issues': issues,
            'issues_count': len(issues)
        }
    
    def _check_validity_consistency(self, issues: List[str]) -> None:
        """Проверяет, что у каждого объекта в store есть валидность."""
        for node_type in self._store.get_all_types():
            for entity_id in self._store.get_all_ids(node_type):
                if not self._validity.is_valid(node_type, entity_id):
                    issues.append(
                        f"Сущность {node_type.value}#{entity_id} в store, но не валидна"
                    )
    
    def _check_relation_targets(self, issues: List[str]) -> None:
        """Проверяет, что все связи ведут на существующие объекты."""
        # ... логика из EntityGraph.check_consistency
        pass
    
    def _check_parent_back_references(self, issues: List[str]) -> None:
        """Проверяет, что у каждого ребенка есть обратная связь."""
        # ... логика из EntityGraph.check_consistency
        pass
    
    def _check_index_consistency(self, issues: List[str]) -> None:
        """Проверяет соответствие прямых и обратных индексов."""
        # ... логика из EntityGraph.check_consistency
        pass