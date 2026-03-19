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
    from utils.logger import get_logger
    log = get_logger(__name__)
    
    child_type = _CHILD_TYPE_MAP.get(parent_type)
    log.debug(f"🔽 get_child_type({parent_type}) = {child_type}")
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
    from utils.logger import get_logger
    log = get_logger(__name__)
    
    parent_type = _PARENT_TYPE_MAP.get(child_type)
    log.debug(f"🔼 get_parent_type({child_type}) = {parent_type}")
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
    from utils.logger import get_logger
    log = get_logger(__name__)
    
    result = _CAN_HAVE_CHILDREN.get(node_type, False)
    log.debug(f"🔍 can_have_children({node_type}) = {result}")
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
    from utils.logger import get_logger
    log = get_logger(__name__)
    
    ancestors = []
    current = get_parent_type(start_type)
    
    while current is not None:
        ancestors.append(current)
        current = get_parent_type(current)
    
    log.debug(f"📊 get_all_ancestors({start_type}) = {[a.value for a in ancestors]}")
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
    from utils.logger import get_logger
    log = get_logger(__name__)
    
    descendants = []
    current = get_child_type(start_type)
    
    while current is not None:
        descendants.append(current)
        current = get_child_type(current)
    
    log.debug(f"📊 get_all_descendants({start_type}) = {[d.value for d in descendants]}")
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
        - debug: результат проверки
    """
    expected_child = get_child_type(parent_type)
    result = expected_child == child_type
    
    from utils.logger import get_logger
    log = get_logger(__name__)
    
    if result:
        log.debug(f"✅ validate_hierarchy: {parent_type} → {child_type} допустимо")
    else:
        log.warning(f"⚠️ validate_hierarchy: {parent_type} → {child_type} НЕДОПУСТИМО")
    
    return result