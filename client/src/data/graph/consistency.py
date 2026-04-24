# client/src/data/graph/consistency.py
"""
Проверка консистентности графа.

Вынесено из EntityGraph для соблюдения SRP.
Проверяет целостность всех индексов и связей между сущностями.

TECHNICAL DEBT:
    - Реализовать _check_relation_targets — проверка связей на существующие объекты
    - Реализовать _check_parent_back_references — проверка обратных связей у детей
    - Реализовать _check_index_consistency — проверка соответствия прямых и обратных индексов
"""

# ===== ИМПОРТЫ =====
from typing import Any, Dict, List

from src.core.rules.hierarchy import get_child_type
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

    TECHNICAL DEBT:
        - Реализовать _check_relation_targets
        - Реализовать _check_parent_back_references
        - Реализовать _check_index_consistency
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, store, relations, validity) -> None:
        """Инициализирует проверяльщик консистентности."""
        log.system("ConsistencyChecker инициализация")
        self._store = store
        self._relations = relations
        self._validity = validity
        log.system("ConsistencyChecker инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    def check(self) -> Dict[str, Any]:
        """Выполняет полную проверку консистентности."""
        log.debug("Запуск проверки консистентности графа")
        issues = []

        self._check_validity_consistency(issues)
        self._check_relation_targets(issues)
        self._check_parent_back_references(issues)
        self._check_index_consistency(issues)

        is_consistent = len(issues) == 0
        if is_consistent:
            log.debug("Проверка консистентности: ошибок не найдено")
        else:
            log.warning(f"Проверка консистентности: найдено {len(issues)} проблем")

        return {
            'consistent': is_consistent,
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
        """
        Проверяет, что все связи ведут на существующие объекты.

        TODO: Реализовать проверку
        - Пройти по всем связям в _relations
        - Проверить, что parent существует в store
        - Проверить, что child существует в store
        """
        pass

    def _check_parent_back_references(self, issues: List[str]) -> None:
        """
        Проверяет, что у каждого ребенка есть обратная связь.

        TODO: Реализовать проверку
        - Пройти по всем детям в _relations
        - Убедиться, что у каждого есть запись в обратном индексе
        """
        pass

    def _check_index_consistency(self, issues: List[str]) -> None:
        """
        Проверяет соответствие прямых и обратных индексов.

        TODO: Реализовать проверку
        - Для каждого parent в прямом индексе
        - Проверить, что каждый child имеет обратную ссылку на этого parent
        """
        pass