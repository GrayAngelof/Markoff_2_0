# client/src/data/graph/relations.py
"""
Индекс связей между сущностями.

RelationIndex обеспечивает O(1) доступ к иерархии "родитель-потомок".
Работает только с ID, не требует наличия объектов в памяти.
Потокобезопасен (RLock).

Прямые индексы: parent_type → {parent_id: set(child_ids)}
Обратные индексы: child_type → {child_id: (parent_type, parent_id)}

Потребители: 
    - entity_graph.py (фасад) — через публичные методы
"""

# ===== ИМПОРТЫ =====
from threading import RLock
from typing import Dict, Set, List, Optional, Tuple, Final, TypedDict

from src.core.types import NodeType
from src.shared.validation import validate_positive_int
from .schema import get_child_type, get_parent_type
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)

# Типы, которые могут быть родителями (физическая иерархия)
_PARENT_TYPES: Final[list[NodeType]] = [
    NodeType.COMPLEX,      # дети: BUILDING
    NodeType.BUILDING,     # дети: FLOOR
    NodeType.FLOOR,        # дети: ROOM
]

# Типы, которые могут быть детьми
_CHILD_TYPES: Final[list[NodeType]] = [
    NodeType.BUILDING,           # родитель: COMPLEX
    NodeType.FLOOR,              # родитель: BUILDING
    NodeType.ROOM,               # родитель: FLOOR
]

# Шаблоны сообщений логирования
_LOG_LINK = "Связь установлена: {child_type}#{child_id} → {parent_type}#{parent_id}"
_LOG_UNLINK = "Связь удалена: {child_type}#{child_id}"
_LOG_REMOVE_NODE = "Узел удален: {node_type}#{node_id} (удалено {children_count} связей)"


# ===== ТИПЫ =====
class RelationStats(TypedDict):
    """Статистика индекса связей."""
    parent_entries: int  # Количество родителей в индексе
    child_entries: int   # Количество детей в индексе
    parent_types: int    # Количество типов родителей, имеющих детей
    child_types: int     # Количество типов детей, имеющих родителей


# ===== ВНУТРЕННИЕ ФУНКЦИИ =====
def _validate_relations_schema() -> None:
    """
    Проверяет согласованность _PARENT_TYPES и _CHILD_TYPES со схемой.

    Убеждается, что каждый родительский тип имеет соответствующий дочерний,
    и наоборот. Вызывается при импорте модуля.
    """
    for parent_type in _PARENT_TYPES:
        child_type = get_child_type(parent_type)
        if child_type is None:
            log.error(
                f"Тип {parent_type.value} помечен как родитель, "
                f"но get_child_type() вернул None"
            )
            raise RuntimeError(
                f"Ошибка конфигурации: {parent_type.value} не может иметь детей "
                f"согласно core.hierarchy"
            )
        if child_type not in _CHILD_TYPES:
            log.warning(
                f"Тип {child_type.value} не в _CHILD_TYPES, "
                f"хотя является ребенком {parent_type.value}"
            )

    for child_type in _CHILD_TYPES:
        parent_type = get_parent_type(child_type)
        if parent_type is None:
            log.error(
                f"Тип {child_type.value} помечен как ребенок, "
                f"но get_parent_type() вернул None"
            )
            raise RuntimeError(
                f"Ошибка конфигурации: {child_type.value} не может иметь родителя "
                f"согласно core.hierarchy"
            )
        if parent_type not in _PARENT_TYPES:
            log.warning(
                f"Тип {parent_type.value} не в _PARENT_TYPES, "
                f"хотя является родителем {child_type.value}"
            )

    log.system(f"RelationIndex схема валидна: {len(_CHILD_TYPES)} типов")


_validate_relations_schema()


# ===== КЛАСС =====
class RelationIndex:
    """
    Потокобезопасный индекс связей между сущностями.

    Все операции O(1) или амортизированное O(1).
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self) -> None:
        """Инициализирует пустые индексы для всех поддерживаемых типов."""
        log.system("RelationIndex инициализация")
        self._lock = RLock()

        # Прямые индексы: parent_type → {parent_id: set(child_ids)}
        self._children: Dict[NodeType, Dict[int, Set[int]]] = {
            parent_type: {} for parent_type in _PARENT_TYPES
        }

        # Обратные индексы: child_type → {child_id: (parent_type, parent_id)}
        self._parents: Dict[NodeType, Dict[int, Tuple[NodeType, int]]] = {
            child_type: {} for child_type in _CHILD_TYPES
        }

        log.system(
            f"RelationIndex инициализирован: "
            f"родителей={len(_PARENT_TYPES)}, детей={len(_CHILD_TYPES)}"
        )

    def clear(self) -> None:
        """Полностью очищает все индексы."""
        with self._lock:
            for parent_type in self._children:
                self._children[parent_type].clear()
            for child_type in self._parents:
                self._parents[child_type].clear()

            log.cache("RelationIndex очищен")

    def get_stats(self) -> RelationStats:
        """Возвращает статистику использования индексов."""
        with self._lock:
            total_parent_entries = sum(
                len(store) for store in self._children.values()
            )
            total_child_entries = sum(
                len(store) for store in self._parents.values()
            )

            parent_types_count = sum(
                1 for store in self._children.values() if store
            )

            child_types_count = sum(
                1 for store in self._parents.values() if store
            )

            return RelationStats(
                parent_entries=total_parent_entries,
                child_entries=total_child_entries,
                parent_types=parent_types_count,
                child_types=child_types_count,
            )

    # ---- УПРАВЛЕНИЕ СВЯЗЯМИ ----
    def link(
        self,
        child_type: NodeType,
        child_id: int,
        parent_type: NodeType,
        parent_id: int,
    ) -> None:
        """
        Устанавливает связь родитель-потомок.

        Если связь уже существовала, она будет перезаписана.

        Raises:
            ValidationError: ID не положительный
            KeyError: Тип не поддерживается
            ValueError: Связь недопустима по иерархии
        """
        child_id = validate_positive_int(child_id, "child_id")
        parent_id = validate_positive_int(parent_id, "parent_id")

        with self._lock:
            if child_type not in self._parents:
                log.error(f"Неподдерживаемый тип ребенка {child_type}")
                raise KeyError(f"Тип {child_type} не поддерживается RelationIndex")

            if parent_type not in self._children:
                log.error(f"Неподдерживаемый тип родителя {parent_type}")
                raise KeyError(f"Тип {parent_type} не поддерживается RelationIndex")

            expected_parent = get_parent_type(child_type)
            if expected_parent and expected_parent != parent_type:
                log.error(
                    f"Недопустимая связь: {child_type.value} → {parent_type.value} "
                    f"(ожидался {expected_parent.value})"
                )
                raise ValueError(
                    f"Недопустимая связь: {child_type.value} не может быть "
                    f"ребенком {parent_type.value}"
                )

            # Удаляем старую связь, если была
            self.unlink(child_type, child_id)

            # Добавляем в прямые индексы
            if parent_id not in self._children[parent_type]:
                self._children[parent_type][parent_id] = set()
            self._children[parent_type][parent_id].add(child_id)

            # Добавляем в обратные индексы
            self._parents[child_type][child_id] = (parent_type, parent_id)

            log.debug(_LOG_LINK.format(
                child_type=child_type.value,
                child_id=child_id,
                parent_type=parent_type.value,
                parent_id=parent_id,
            ))

    def unlink(self, child_type: NodeType, child_id: int) -> bool:
        """
        Удаляет связь для потомка.

        Returns:
            True если связь была удалена, False если не существовала
        """
        child_id = validate_positive_int(child_id, "child_id")

        with self._lock:
            if child_type not in self._parents:
                return False

            parent_info = self._parents[child_type].get(child_id)
            if not parent_info:
                return False

            parent_type, parent_id = parent_info

            # Удаляем из прямых индексов
            if parent_type in self._children and parent_id in self._children[parent_type]:
                self._children[parent_type][parent_id].discard(child_id)
                # Если множество стало пустым — удаляем ключ
                if not self._children[parent_type][parent_id]:
                    del self._children[parent_type][parent_id]

            # Удаляем из обратных индексов
            del self._parents[child_type][child_id]

            log.debug(_LOG_UNLINK.format(
                child_type=child_type.value,
                child_id=child_id,
            ))
            return True

    def remove_node(self, node_type: NodeType, node_id: int) -> None:
        """
        Удаляет все связи, связанные с узлом.

        Если узел — родитель: удаляет всех его детей.
        Если узел — ребенок: удаляет его связь с родителем.
        """
        node_id = validate_positive_int(node_id, "node_id")

        with self._lock:
            removed_children = 0

            # Удаляем как родителя
            if node_type in self._children:
                children_ids = self.get_children(node_type, node_id)
                child_type = get_child_type(node_type)

                if child_type and child_type in self._parents:
                    for child_id in children_ids:
                        if child_id in self._parents[child_type]:
                            del self._parents[child_type][child_id]
                            removed_children += 1

                if node_id in self._children[node_type]:
                    del self._children[node_type][node_id]

            # Удаляем как ребенка
            if node_type in self._parents:
                if node_id in self._parents[node_type]:
                    del self._parents[node_type][node_id]

            log.debug(_LOG_REMOVE_NODE.format(
                node_type=node_type.value,
                node_id=node_id,
                children_count=removed_children,
            ))

    # ---- НАВИГАЦИЯ ----
    def get_children(self, parent_type: NodeType, parent_id: int) -> List[int]:
        """
        Возвращает ID всех дочерних элементов.

        Порядок элементов не гарантирован.
        """
        parent_id = validate_positive_int(parent_id, "parent_id")

        with self._lock:
            if parent_type not in self._children:
                log.error(f"Неподдерживаемый тип {parent_type}")
                raise KeyError(f"Тип {parent_type} не поддерживается RelationIndex")

            children_set = self._children[parent_type].get(parent_id)
            return list(children_set) if children_set else []

    def get_parent(
        self,
        child_type: NodeType,
        child_id: int,
    ) -> Optional[Tuple[NodeType, int]]:
        """
        Возвращает информацию о родителе в формате (parent_type, parent_id).

        Returns:
            None если у узла нет родителя
        """
        child_id = validate_positive_int(child_id, "child_id")

        with self._lock:
            if child_type not in self._parents:
                log.error(f"Неподдерживаемый тип {child_type}")
                raise KeyError(f"Тип {child_type} не поддерживается RelationIndex")

            return self._parents[child_type].get(child_id)

    def has_children(self, parent_type: NodeType, parent_id: int) -> bool:
        """Проверяет, есть ли у родителя хотя бы один ребенок."""
        parent_id = validate_positive_int(parent_id, "parent_id")

        with self._lock:
            if parent_type not in self._children:
                log.error(f"Неподдерживаемый тип {parent_type}")
                raise KeyError(f"Тип {parent_type} не поддерживается RelationIndex")

            children_set = self._children[parent_type].get(parent_id)
            return children_set is not None and bool(children_set)