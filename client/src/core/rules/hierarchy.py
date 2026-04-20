# client/src/core/rules/hierarchy.py
"""
Правила иерархии объектов.

Определяет связи между типами физической структуры:
- Кто кому родитель
- Кто может иметь детей
- Навигация по иерархии (предки, потомки)

Зависит только от types.nodes — никаких других модулей!
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional

from src.core.types.nodes import NodeType
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)

# Карта: родитель → тип ребёнка
_CHILD_TYPE_MAP = {
    NodeType.COMPLEX: NodeType.BUILDING,
    NodeType.BUILDING: NodeType.FLOOR,
    NodeType.FLOOR: NodeType.ROOM,
    NodeType.ROOM: None,
}

# Карта: ребёнок → тип родителя
_PARENT_TYPE_MAP = {
    NodeType.COMPLEX: None,
    NodeType.BUILDING: NodeType.COMPLEX,
    NodeType.FLOOR: NodeType.BUILDING,
    NodeType.ROOM: NodeType.FLOOR,
}

# Карта: может ли тип иметь детей
_CAN_HAVE_CHILDREN = {
    NodeType.COMPLEX: True,
    NodeType.BUILDING: True,
    NodeType.FLOOR: True,
    NodeType.ROOM: False,
}


# ===== ПУБЛИЧНЫЕ ФУНКЦИИ =====
def get_child_type(parent_type: NodeType) -> Optional[NodeType]:
    """
    Возвращает тип дочернего элемента для указанного родителя.

    Returns:
        None если узел листовой (не может иметь детей)
    """
    return _CHILD_TYPE_MAP.get(parent_type)


def get_parent_type(child_type: NodeType) -> Optional[NodeType]:
    """
    Возвращает тип родителя для указанного дочернего узла.

    Returns:
        None если узел корневой (не имеет родителя)
    """
    return _PARENT_TYPE_MAP.get(child_type)


def can_have_children(node_type: NodeType) -> bool:
    """Проверяет, может ли узел указанного типа иметь детей."""
    return _CAN_HAVE_CHILDREN.get(node_type, False)


def is_leaf(node_type: NodeType) -> bool:
    """Проверяет, является ли узел листом (не может иметь детей)."""
    return not can_have_children(node_type)


def get_all_ancestors(start_type: NodeType) -> List[NodeType]:
    """
    Возвращает всех предков для указанного типа.

    Returns:
        Список типов предков от ближайшего к дальнему.
        Например, для ROOM → [FLOOR, BUILDING, COMPLEX]
    """
    ancestors = []
    current = get_parent_type(start_type)

    while current is not None:
        ancestors.append(current)
        current = get_parent_type(current)

    return ancestors


def get_all_descendants(start_type: NodeType) -> List[NodeType]:
    """
    Возвращает всех потомков для указанного типа.

    Returns:
        Список типов потомков.
        Например, для COMPLEX → [BUILDING, FLOOR, ROOM]
    """
    descendants = []
    current = get_child_type(start_type)

    while current is not None:
        descendants.append(current)
        current = get_child_type(current)

    return descendants


def validate_hierarchy(parent_type: NodeType, child_type: NodeType) -> bool:
    """Проверяет, допустима ли связь родитель-потомок."""
    expected_child = get_child_type(parent_type)
    is_valid = expected_child == child_type

    if is_valid:
        log.debug(f"Связь допустима: {parent_type.value} → {child_type.value}")
    else:
        log.warning(f"Связь недопустима: {parent_type.value} → {child_type.value}")

    return is_valid