# client/src/data/graph/consistency.py
"""
Проверка консистентности графа.

Вынесено из EntityGraph для соблюдения SRP.
Проверяет целостность всех индексов и связей между сущностями.
"""

# ===== ИМПОРТЫ =====
from typing import Any, Dict, List

from src.core.hierarchy import get_child_type
from src.core.types import NodeType
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class ConsistencyChecker:
    """
    Проверяет консистентность всех индексов графа.

    Выявляет:
    - Сущности в store, но не валидные
    - Связи, указывающие на несуществующие объекты
    - Висячие объекты без связей
    - Несоответствие прямых и обратных индексов
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, store, relations, validity) -> None:
        self._store = store
        self._relations = relations
        self._validity = validity

    # ---- ПУБЛИЧНОЕ API ----
    def check(self) -> Dict[str, Any]:
        """Выполняет полную проверку консистентности."""
        issues = []

        self._check_validity_consistency(issues)
        self._check_relation_targets(issues)
        self._check_parent_back_references(issues)
        self._check_index_consistency(issues)

        return {
            'consistent': len(issues) == 0,
            'issues': issues,
            'issues_count': len(issues),
        }

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
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
        # TODO: реализовать проверку
        pass

    def _check_parent_back_references(self, issues: List[str]) -> None:
        """Проверяет, что у каждого ребенка есть обратная связь."""
        # TODO: реализовать проверку
        pass

    def _check_index_consistency(self, issues: List[str]) -> None:
        """Проверяет соответствие прямых и обратных индексов."""
        # TODO: реализовать проверку
        pass