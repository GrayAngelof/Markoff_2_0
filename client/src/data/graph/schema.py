# client/src/data/graph/schema.py (расширенная версия)
"""
Схема графа - единственное место, где описана структура иерархии.
Теперь содержит ВСЕ правила для автоматического построения индексов.
"""
from typing import Dict, Optional, Any, Type, List, Callable
from dataclasses import fields

from src.data.entity_types import (
    NodeType, COMPLEX, BUILDING, FLOOR, ROOM,
    MODEL_TO_NODETYPE, NODETYPE_TO_MODEL
)
from src.models import Complex, Building, Floor, Room
from utils.logger import get_logger


log = get_logger(__name__)


class GraphSchema:
    """
    Схема графа - описывает структуру иерархии декларативно.
    Все правила в одном месте.
    """
    
    # Определение иерархии (кто чей родитель)
    PARENT_OF: Dict[NodeType, Optional[NodeType]] = {
        COMPLEX: None,      # комплекс - корень
        BUILDING: COMPLEX,   # корпус принадлежит комплексу
        FLOOR: BUILDING,     # этаж принадлежит корпусу
        ROOM: FLOOR,         # комната принадлежит этажу
    }
    
    # Поля, содержащие ID родителя
    PARENT_ID_FIELD: Dict[NodeType, Optional[str]] = {
        COMPLEX: None,
        BUILDING: "complex_id",
        FLOOR: "building_id",
        ROOM: "floor_id",
    }
    
    # Какие типы могут иметь детей (не листья)
    CAN_HAVE_CHILDREN: Dict[NodeType, bool] = {
        COMPLEX: True,
        BUILDING: True,
        FLOOR: True,
        ROOM: False,
    }
    
    # Порядок в иерархии (для обходов)
    HIERARCHY_ORDER: List[NodeType] = [
        COMPLEX,
        BUILDING,
        FLOOR,
        ROOM,
    ]
    
    @classmethod
    def get_parent_type(cls, child_type: NodeType) -> Optional[NodeType]:
        """Возвращает тип родителя."""
        return cls.PARENT_OF.get(child_type)
    
    @classmethod
    def get_child_type(cls, parent_type: NodeType) -> Optional[NodeType]:
        """Возвращает тип дочернего элемента."""
        # Инвертируем PARENT_OF
        for child, parent in cls.PARENT_OF.items():
            if parent == parent_type:
                return child
        return None
    
    @classmethod
    def get_parent_id(cls, entity: Any) -> Optional[int]:
        """Извлекает ID родителя из сущности."""
        node_type = MODEL_TO_NODETYPE.get(type(entity))
        if not node_type:
            return None
        
        field_name = cls.PARENT_ID_FIELD.get(node_type)
        if not field_name:
            return None
        
        return getattr(entity, field_name, None)
    
    @classmethod
    def get_node_type(cls, entity: Any) -> Optional[NodeType]:
        """Определяет тип сущности."""
        return MODEL_TO_NODETYPE.get(type(entity))
    
    @classmethod
    def get_model_class(cls, node_type: NodeType) -> Optional[Type]:
        """Возвращает класс модели."""
        return NODETYPE_TO_MODEL.get(node_type)
    
    @classmethod
    def can_have_children(cls, node_type: NodeType) -> bool:
        """Может ли узел иметь детей."""
        return cls.CAN_HAVE_CHILDREN.get(node_type, False)
    
    @classmethod
    def is_root(cls, node_type: NodeType) -> bool:
        """Является ли узел корневым."""
        return cls.PARENT_OF.get(node_type) is None
    
    @classmethod
    def is_leaf(cls, node_type: NodeType) -> bool:
        """Является ли узел листом."""
        return not cls.can_have_children(node_type)
    
    @classmethod
    def get_path_to_root(cls, node_type: NodeType) -> List[NodeType]:
        """
        Возвращает путь от узла до корня.
        Например: ROOM -> [FLOOR, BUILDING, COMPLEX]
        """
        path = []
        current = node_type
        
        while current is not None:
            path.append(current)
            current = cls.get_parent_type(current)
        
        return path[1:]  # исключаем сам узел
    
    @classmethod
    def validate_entity(cls, entity: Any) -> bool:
        """
        Проверяет, соответствует ли сущность схеме.
        Используется для отладки.
        """
        node_type = cls.get_node_type(entity)
        if not node_type:
            log.error(f"Неизвестный тип сущности: {type(entity)}")
            return False
        
        # Проверяем наличие родительского ID если должен быть
        parent_field = cls.PARENT_ID_FIELD.get(node_type)
        if parent_field and not hasattr(entity, parent_field):
            log.error(f"Сущность {node_type} не имеет поля {parent_field}")
            return False
        
        return True


# Для обратной совместимости экспортируем удобные функции
get_parent_type = GraphSchema.get_parent_type
get_child_type = GraphSchema.get_child_type
get_parent_id = GraphSchema.get_parent_id
get_node_type = GraphSchema.get_node_type
get_model_class = GraphSchema.get_model_class
can_have_children = GraphSchema.can_have_children
is_root = GraphSchema.is_root
is_leaf = GraphSchema.is_leaf
get_path_to_root = GraphSchema.get_path_to_root

log.debug("GraphSchema initialized")