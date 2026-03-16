# client/src/data/__init__.py
"""
Пакет для работы с данными клиента.
Предоставляет граф сущностей и типы узлов.
"""
# Сначала импортируем типы (они не зависят от graph)
from src.data.entity_types import (
    NodeType, COMPLEX, BUILDING, FLOOR, ROOM,
    MODEL_TO_NODETYPE, NODETYPE_TO_MODEL
)

# Потом импортируем граф (он зависит от типов)
from src.data.entity_graph import EntityGraph

# И только потом импортируем компоненты graph (они тоже зависят от типов)
from src.data.graph import (
    EntityStore, RelationIndex, ValidityIndex,
    get_child_type, get_parent_type, get_parent_id, get_node_type,
    get_model_class
)

__all__ = [
    # Основной фасад
    "EntityGraph",
    
    # Типы узлов (КОНСТАНТЫ ЗДЕСЬ!)
    "NodeType",
    "COMPLEX",
    "BUILDING", 
    "FLOOR",
    "ROOM",
    
    # Маппинги (для продвинутого использования)
    "MODEL_TO_NODETYPE",
    "NODETYPE_TO_MODEL",
    
    # Компоненты (для тестирования и расширения)
    "EntityStore",
    "RelationIndex",
    "ValidityIndex",
    
    # Утилиты навигации
    "get_child_type",
    "get_parent_type",
    "get_parent_id",
    "get_node_type",
    "get_model_class",
]