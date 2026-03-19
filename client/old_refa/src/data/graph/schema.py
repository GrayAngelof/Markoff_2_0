# client/src/data/graph/schema.py
"""
Схема графа - единственное место, где описана структура иерархии.
Импортирует константы из entity_types.py
"""
from typing import Dict, Optional, Any, Type

from src.data.entity_types import (
    NodeType, COMPLEX, BUILDING, FLOOR, ROOM,
    COUNTERPARTY, RESPONSIBLE_PERSON,
    MODEL_TO_NODETYPE, NODETYPE_TO_MODEL,
    CLASS_NAME_TO_NODETYPE  # <-- ИСПРАВЛЕНО
)
from src.models import Complex, Building, Floor, Room
from src.models.counterparty import Counterparty
from src.models.responsible_person import ResponsiblePerson
from utils.logger import get_logger


log = get_logger(__name__)


# Словарь для навигации по иерархии вниз
CHILD_TYPE_MAP: Dict[NodeType, Optional[NodeType]] = {
    COMPLEX: BUILDING,
    BUILDING: FLOOR,
    FLOOR: ROOM,
    ROOM: None,  # лист
    COUNTERPARTY: RESPONSIBLE_PERSON,  # контрагент может иметь ответственных лиц
    RESPONSIBLE_PERSON: None,  # ответственное лицо - лист
}

# Словарь для навигации по иерархии вверх
PARENT_TYPE_MAP: Dict[NodeType, Optional[NodeType]] = {
    COMPLEX: None,  # корень
    BUILDING: COMPLEX,
    FLOOR: BUILDING,
    ROOM: FLOOR,
    COUNTERPARTY: None,  # контрагент может быть корнем (владелец)
    RESPONSIBLE_PERSON: COUNTERPARTY,
}

# Поле, содержащее ID родителя для каждого типа
PARENT_ID_FIELD: Dict[NodeType, Optional[str]] = {
    COMPLEX: None,
    BUILDING: "complex_id",
    FLOOR: "building_id",
    ROOM: "floor_id",
    COUNTERPARTY: None,
    RESPONSIBLE_PERSON: "counterparty_id",
}


def get_child_type(parent_type: NodeType) -> Optional[NodeType]:
    """Возвращает тип дочернего элемента для данного родителя."""
    return CHILD_TYPE_MAP.get(parent_type)


def get_parent_type(child_type: NodeType) -> Optional[NodeType]:
    """Возвращает тип родителя для данного дочернего элемента."""
    return PARENT_TYPE_MAP.get(child_type)


def get_parent_id(entity: Any) -> Optional[int]:
    """
    Извлекает ID родителя из сущности.
    Универсальный метод, заменяющий кучу if-elif.
    """
    # Получаем тип по классу
    node_type = MODEL_TO_NODETYPE.get(type(entity))
    if not node_type:
        # Пробуем получить по имени класса
        class_name = type(entity).__name__
        node_type = CLASS_NAME_TO_NODETYPE.get(class_name)
        if not node_type:
            return None
    
    field_name = PARENT_ID_FIELD.get(node_type)
    if not field_name:
        return None
    
    return getattr(entity, field_name, None)


def get_node_type(entity: Any) -> Optional[NodeType]:
    """Определяет NodeType по классу сущности."""
    node_type = MODEL_TO_NODETYPE.get(type(entity))
    if node_type:
        return node_type
    
    # Пробуем по имени класса
    class_name = type(entity).__name__
    return CLASS_NAME_TO_NODETYPE.get(class_name)


def get_model_class(node_type: NodeType) -> Optional[Type]:
    """Возвращает класс модели для типа узла."""
    return NODETYPE_TO_MODEL.get(node_type)


log.debug("Graph schema initialized")