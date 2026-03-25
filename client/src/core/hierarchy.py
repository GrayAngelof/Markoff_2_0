# client/src/core/hierarchy.py
"""
ПРАВИЛА ИЕРАРХИИ ОБЪЕКТОВ.

Содержит бизнес-логику определения связей между типами:
- Кто кому родитель
- Кто может иметь детей
- Навигация по иерархии

Зависит только от types.nodes (никаких других модулей!)
"""
from typing import Optional, List

from .types import NodeType

# ===== Конфигурация иерархии =====
# (внутренние константы, не экспортируются)

_CHILD_TYPE_MAP = {
    NodeType.COMPLEX: NodeType.BUILDING,
    NodeType.BUILDING: NodeType.FLOOR,
    NodeType.FLOOR: NodeType.ROOM,
    NodeType.ROOM: None,
    NodeType.COUNTERPARTY: NodeType.RESPONSIBLE_PERSON,
    NodeType.RESPONSIBLE_PERSON: None,
}

_PARENT_TYPE_MAP = {
    NodeType.COMPLEX: None,
    NodeType.BUILDING: NodeType.COMPLEX,
    NodeType.FLOOR: NodeType.BUILDING,
    NodeType.ROOM: NodeType.FLOOR,
    NodeType.COUNTERPARTY: None,
    NodeType.RESPONSIBLE_PERSON: NodeType.COUNTERPARTY,
}

_CAN_HAVE_CHILDREN = {
    NodeType.COMPLEX: True,
    NodeType.BUILDING: True,
    NodeType.FLOOR: True,
    NodeType.ROOM: False,
    NodeType.COUNTERPARTY: True,
    NodeType.RESPONSIBLE_PERSON: False,
}

# ===== Логгер =====
from utils.logger import get_logger
_log = get_logger(__name__)


# ===== Публичные функции =====

def get_child_type(parent_type: NodeType) -> Optional[NodeType]:
    """
    Возвращает тип дочернего элемента для указанного родителя.
    
    Args:
        parent_type: Тип родительского узла
        
    Returns:
        Optional[NodeType]: Тип детей или None, если узел листовой
        
    Пример:
        >>> get_child_type(NodeType.COMPLEX)
        <NodeType.BUILDING: 'building'>
        >>> get_child_type(NodeType.ROOM) is None
        True
        
    Логирование:
        - debug: результат поиска
    """
    child_type = _CHILD_TYPE_MAP.get(parent_type)
    _log.debug(f"get_child_type({parent_type.value}) = {child_type.value if child_type else None}")
    return child_type


def get_parent_type(child_type: NodeType) -> Optional[NodeType]:
    """
    Возвращает тип родителя для указанного дочернего узла.
    
    Args:
        child_type: Тип дочернего узла
        
    Returns:
        Optional[NodeType]: Тип родителя или None, если узел корневой
        
    Пример:
        >>> get_parent_type(NodeType.BUILDING)
        <NodeType.COMPLEX: 'complex'>
        >>> get_parent_type(NodeType.COMPLEX) is None
        True
        
    Логирование:
        - debug: результат поиска
    """
    parent_type = _PARENT_TYPE_MAP.get(child_type)
    # _log.debug(f"get_parent_type({child_type.value}) = {parent_type.value if parent_type else None}")
    return parent_type


def can_have_children(node_type: NodeType) -> bool:
    """
    Проверяет, может ли узел указанного типа иметь детей.
    
    Args:
        node_type: Тип узла
        
    Returns:
        bool: True если узел может иметь детей
        
    Пример:
        >>> can_have_children(NodeType.COMPLEX)
        True
        >>> can_have_children(NodeType.ROOM)
        False
        
    Логирование:
        - debug: результат проверки
    """
    result = _CAN_HAVE_CHILDREN.get(node_type, False)
    _log.debug(f"can_have_children({node_type.value}) = {result}")
    return result


def is_leaf(node_type: NodeType) -> bool:
    """
    Проверяет, является ли узел листом (не может иметь детей).
    
    Args:
        node_type: Тип узла
        
    Returns:
        bool: True если узел листовой
        
    Пример:
        >>> is_leaf(NodeType.ROOM)
        True
        >>> is_leaf(NodeType.COMPLEX)
        False
    """
    return not can_have_children(node_type)


def get_all_ancestors(start_type: NodeType) -> List[NodeType]:
    """
    Возвращает всех предков для указанного типа.
    
    Args:
        start_type: Начальный тип
        
    Returns:
        List[NodeType]: Список типов предков (от ближайшего к дальнему)
        
    Пример:
        >>> get_all_ancestors(NodeType.ROOM)
        [NodeType.FLOOR, NodeType.BUILDING, NodeType.COMPLEX]
        
    Логирование:
        - debug: найденные предки
    """
    ancestors = []
    current = get_parent_type(start_type)
    
    while current is not None:
        ancestors.append(current)
        current = get_parent_type(current)
    
    _log.debug(f"get_all_ancestors({start_type.value}) = {[a.value for a in ancestors]}")
    return ancestors


def get_all_descendants(start_type: NodeType) -> List[NodeType]:
    """
    Возвращает всех потомков для указанного типа.
    
    Args:
        start_type: Начальный тип
        
    Returns:
        List[NodeType]: Список типов потомков
        
    Пример:
        >>> get_all_descendants(NodeType.COMPLEX)
        [NodeType.BUILDING, NodeType.FLOOR, NodeType.ROOM]
        
    Логирование:
        - debug: найденные потомки
    """
    descendants = []
    current = get_child_type(start_type)
    
    while current is not None:
        descendants.append(current)
        current = get_child_type(current)
    
    _log.debug(f"get_all_descendants({start_type.value}) = {[d.value for d in descendants]}")
    return descendants


def validate_hierarchy(parent_type: NodeType, child_type: NodeType) -> bool:
    """
    Проверяет, допустима ли связь родитель-потомок.
    
    Args:
        parent_type: Тип родителя
        child_type: Тип потомка
        
    Returns:
        bool: True если связь допустима
        
    Пример:
        >>> validate_hierarchy(NodeType.COMPLEX, NodeType.BUILDING)
        True
        >>> validate_hierarchy(NodeType.BUILDING, NodeType.COMPLEX)
        False
        
    Логирование:
        - debug: для допустимых связей
        - warning: для недопустимых связей
    """
    expected_child = get_child_type(parent_type)
    result = expected_child == child_type
    
    if result:
        _log.debug(f"validate_hierarchy: {parent_type.value} → {child_type.value} допустимо")
    else:
        _log.warning(f"validate_hierarchy: {parent_type.value} → {child_type.value} недопустимо")
    
    return result