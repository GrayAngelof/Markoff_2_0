"""
Индекс связей между сущностями — быстрый доступ к иерархии.

Это третий компонент Data слоя (после schema и store).
RelationIndex отвечает только за одно: хранить связи "родитель-потомок"
и предоставлять быстрый O(1) доступ к ним.

Принципы:
    - Прямые индексы: parent_type → {parent_id: set(child_ids)}
    - Обратные индексы: child_type → {child_id: (parent_type, parent_id)}
    - Все операции потокобезопасны (RLock)
    - Связи обновляются автоматически через методы link/unlink

Зависимости:
    - threading — для RLock
    - core.types.NodeType — типы узлов
    - core.hierarchy — get_child_type, get_parent_type
    - shared.validation — validate_positive_int
    - .schema — get_child_type, get_parent_type (обертки)
    - utils.logger — логирование

Потребители:
    - entity_graph.py (фасад) — через публичные методы
    - Никто не должен импортировать relations напрямую!

ВАЖНО:
    RelationIndex не знает о существовании объектов.
    Он работает только с ID (int). Это позволяет:
        - Хранить связи даже если объекты еще не загружены
        - Быстро перестраивать индексы при обновлении
        - Избежать циклических ссылок
"""

from threading import RLock
from typing import Dict, Set, List, Optional, Tuple, Final, TypedDict

from src.core.types import NodeType
from src.shared.validation import validate_positive_int
from .schema import get_child_type, get_parent_type
from utils.logger import get_logger


# ============================================
# КОНСТАНТЫ
# ============================================

# Единый логгер для модуля
log = get_logger(__name__)

# Типы, которые могут быть родителями (имеют детей)
_PARENT_TYPES: Final[list[NodeType]] = [
    NodeType.COMPLEX,      # дети: BUILDING
    NodeType.BUILDING,     # дети: FLOOR
    NodeType.FLOOR,        # дети: ROOM
    NodeType.COUNTERPARTY, # дети: RESPONSIBLE_PERSON
]

# Типы, которые могут быть детьми (имеют родителей)
_CHILD_TYPES: Final[list[NodeType]] = [
    NodeType.BUILDING,           # родитель: COMPLEX
    NodeType.FLOOR,              # родитель: BUILDING
    NodeType.ROOM,               # родитель: FLOOR
    NodeType.RESPONSIBLE_PERSON, # родитель: COUNTERPARTY
]

# Сообщения для логирования
_LOG_LINK = "Связь установлена: {child_type}#{child_id} → {parent_type}#{parent_id}"
_LOG_UNLINK = "Связь удалена: {child_type}#{child_id}"
_LOG_REMOVE_NODE = "Узел удален: {node_type}#{node_id} (удалено {children_count} связей)"


# ============================================
# ТИПЫ ДЛЯ СТАТИСТИКИ
# ============================================

class RelationStats(TypedDict):
    """Статистика индекса связей."""
    parent_entries: int
    child_entries: int
    parent_types: int
    child_types: int


# ============================================
# ВАЛИДАЦИЯ ПРИ ИМПОРТЕ
# ============================================

def _validate_relations_schema() -> None:
    """
    Проверяет, что все типы имеют корректные связи.
    
    Убеждается, что:
        - У каждого родительского типа есть соответствующий дочерний
        - У каждого дочернего типа есть соответствующий родительский
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
    
    log.info("Схема RelationIndex валидна")


# Выполняем валидацию при импорте
_validate_relations_schema()


# ============================================
# КЛАСС RELATION INDEX
# ============================================

class RelationIndex:
    """
    Потокобезопасный индекс связей между сущностями.
    
    Хранит два типа индексов:
        1. Прямые (children) — для быстрого получения всех детей родителя
        2. Обратные (parents) — для быстрого получения родителя ребенка
    
    Все операции O(1) или амортизированное O(1).
    
    Пример:
        >>> idx = RelationIndex()
        >>> idx.link(NodeType.BUILDING, 101, NodeType.COMPLEX, 1)
        >>> idx.get_children(NodeType.COMPLEX, 1)
        [101]
        >>> idx.get_parent(NodeType.BUILDING, 101)
        (NodeType.COMPLEX, 1)
    """
    
    def __init__(self) -> None:
        """Инициализирует пустые индексы."""
        self._lock = RLock()
        
        # Прямые индексы: parent_type → {parent_id: set(child_ids)}
        self._children: Dict[NodeType, Dict[int, Set[int]]] = {
            parent_type: {} for parent_type in _PARENT_TYPES
        }
        
        # Обратные индексы: child_type → {child_id: (parent_type, parent_id)}
        self._parents: Dict[NodeType, Dict[int, Tuple[NodeType, int]]] = {
            child_type: {} for child_type in _CHILD_TYPES
        }
        
        log.info(
            f"RelationIndex инициализирован: "
            f"родителей={len(_PARENT_TYPES)}, детей={len(_CHILD_TYPES)}"
        )
    
    # ============================================
    # УПРАВЛЕНИЕ СВЯЗЯМИ
    # ============================================
    
    def link(self, child_type: NodeType, child_id: int,
             parent_type: NodeType, parent_id: int) -> None:
        """
        Устанавливает связь родитель-потомок.
        
        Если связь уже существовала, она будет перезаписана.
        
        Args:
            child_type: Тип дочернего узла
            child_id: ID дочернего узла (валидируется)
            parent_type: Тип родительского узла
            parent_id: ID родительского узла (валидируется)
            
        Raises:
            ValidationError: Если ID не положительные (из validate_positive_int)
            KeyError: Если child_type или parent_type не поддерживаются
            ValueError: Если связь недопустима по иерархии
        """
        # Валидация ID через общую утилиту
        child_id = validate_positive_int(child_id, "child_id")
        parent_id = validate_positive_int(parent_id, "parent_id")
        
        with self._lock:
            # Проверка поддержки типов (специфичная для RelationIndex)
            if child_type not in self._parents:
                log.error(f"Неподдерживаемый тип ребенка {child_type}")
                raise KeyError(f"Тип {child_type} не поддерживается RelationIndex")
            
            if parent_type not in self._children:
                log.error(f"Неподдерживаемый тип родителя {parent_type}")
                raise KeyError(f"Тип {parent_type} не поддерживается RelationIndex")
            
            # Проверка допустимости связи по схеме (через core)
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
                parent_id=parent_id
            ))
    
    def unlink(self, child_type: NodeType, child_id: int) -> bool:
        """
        Удаляет связь для потомка.
        
        Args:
            child_type: Тип дочернего узла
            child_id: ID дочернего узла (валидируется)
            
        Returns:
            bool: True если связь была удалена, False если не существовала
        """
        # Валидация ID через общую утилиту
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
                # Если множество стало пустым — удаляем ключ (экономия памяти)
                if not self._children[parent_type][parent_id]:
                    del self._children[parent_type][parent_id]
            
            # Удаляем из обратных индексов
            del self._parents[child_type][child_id]
            
            log.debug(_LOG_UNLINK.format(
                child_type=child_type.value,
                child_id=child_id
            ))
            return True
    
    # ============================================
    # НАВИГАЦИЯ
    # ============================================
    
    def get_children(self, parent_type: NodeType, parent_id: int) -> List[int]:
        """
        Возвращает ID всех дочерних элементов.
        
        Args:
            parent_type: Тип родителя
            parent_id: ID родителя (валидируется)
            
        Returns:
            List[int]: Список ID детей (порядок не гарантирован)
            
        Raises:
            ValidationError: Если parent_id не положительный
            KeyError: Если parent_type не поддерживается
        """
        # Валидация ID через общую утилиту
        parent_id = validate_positive_int(parent_id, "parent_id")
        
        with self._lock:
            if parent_type not in self._children:
                log.error(f"Неподдерживаемый тип {parent_type}")
                raise KeyError(f"Тип {parent_type} не поддерживается RelationIndex")
            
            children_set = self._children[parent_type].get(parent_id)
            if children_set is None:
                return []
            
            return list(children_set)
    
    def get_parent(self, child_type: NodeType, child_id: int) -> Optional[Tuple[NodeType, int]]:
        """
        Возвращает информацию о родителе.
        
        Args:
            child_type: Тип дочернего узла
            child_id: ID дочернего узла (валидируется)
            
        Returns:
            Optional[Tuple[NodeType, int]]: (parent_type, parent_id) или None
            
        Raises:
            ValidationError: Если child_id не положительный
            KeyError: Если child_type не поддерживается
        """
        # Валидация ID через общую утилиту
        child_id = validate_positive_int(child_id, "child_id")
        
        with self._lock:
            if child_type not in self._parents:
                log.error(f"Неподдерживаемый тип {child_type}")
                raise KeyError(f"Тип {child_type} не поддерживается RelationIndex")
            
            return self._parents[child_type].get(child_id)
    
    def has_children(self, parent_type: NodeType, parent_id: int) -> bool:
        """
        Проверяет, есть ли у родителя дети.
        
        Args:
            parent_type: Тип родителя
            parent_id: ID родителя (валидируется)
            
        Returns:
            bool: True если есть хотя бы один ребенок
            
        Raises:
            ValidationError: Если parent_id не положительный
            KeyError: Если parent_type не поддерживается
        """
        # Валидация ID через общую утилиту
        parent_id = validate_positive_int(parent_id, "parent_id")
        
        with self._lock:
            if parent_type not in self._children:
                log.error(f"Неподдерживаемый тип {parent_type}")
                raise KeyError(f"Тип {parent_type} не поддерживается RelationIndex")
            
            children_set = self._children[parent_type].get(parent_id)
            return children_set is not None and len(children_set) > 0
    
    # ============================================
    # УДАЛЕНИЕ УЗЛА
    # ============================================
    
    def remove_node(self, node_type: NodeType, node_id: int) -> None:
        """
        Удаляет все связи, связанные с узлом.
        
        Если узел является родителем — удаляет всех его детей из индексов.
        Если узел является ребенком — удаляет его связь с родителем.
        
        Args:
            node_type: Тип узла
            node_id: ID узла (валидируется)
            
        Raises:
            ValidationError: Если node_id не положительный
            KeyError: Если node_type не поддерживается ни как родитель, ни как ребенок
        """
        # Валидация ID через общую утилиту
        node_id = validate_positive_int(node_id, "node_id")
        
        with self._lock:
            removed_children = 0
            
            # Если узел может быть родителем — удаляем всех его детей
            if node_type in self._children:
                children_ids = self.get_children(node_type, node_id)
                child_type = get_child_type(node_type)
                
                if child_type and child_type in self._parents:
                    for child_id in children_ids:
                        if child_id in self._parents[child_type]:
                            del self._parents[child_type][child_id]
                            removed_children += 1
                
                # Удаляем запись о родителе из прямого индекса
                if node_id in self._children[node_type]:
                    del self._children[node_type][node_id]
            
            # Если узел может быть ребенком — удаляем его связь с родителем
            if node_type in self._parents:
                if node_id in self._parents[node_type]:
                    del self._parents[node_type][node_id]
            
            log.debug(_LOG_REMOVE_NODE.format(
                node_type=node_type.value,
                node_id=node_id,
                children_count=removed_children
            ))
    
    # ============================================
    # УПРАВЛЕНИЕ
    # ============================================
    
    def clear(self) -> None:
        """Полностью очищает все индексы."""
        with self._lock:
            for parent_type in self._children:
                self._children[parent_type].clear()
            for child_type in self._parents:
                self._parents[child_type].clear()
            
            log.debug("RelationIndex очищен")
    
    def get_stats(self) -> RelationStats:
        """
        Возвращает статистику индексов.
        
        Returns:
            RelationStats: Статистика использования
        """
        with self._lock:
            total_parent_entries = sum(
                len(store) for store in self._children.values()
            )
            total_child_entries = sum(
                len(store) for store in self._parents.values()
            )
            
            parent_types_count = 0
            for store in self._children.values():
                if store:
                    parent_types_count += 1
            
            child_types_count = 0
            for store in self._parents.values():
                if store:
                    child_types_count += 1
            
            return RelationStats(
                parent_entries=total_parent_entries,
                child_entries=total_child_entries,
                parent_types=parent_types_count,
                child_types=child_types_count,
            )