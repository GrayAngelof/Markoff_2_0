# client/src/data/graph/__init__.py
"""
Пакет компонентов графа сущностей.

Предоставляет модульную структуру для работы с данными.
Все константы типов импортируются из родительского пакета data.
"""
# Импортируем компоненты
from src.data.graph.entity_store import EntityStore
from src.data.graph.relation_index import RelationIndex, ParentInfo
from src.data.graph.validity_index import ValidityIndex

# Импортируем утилиты из schema (они уже используют entity_types)
from src.data.graph.schema import (
    get_child_type,
    get_parent_type,
    get_parent_id,
    get_node_type,
    get_model_class
)

# НЕ импортируем константы COMPLEX, BUILDING и т.д. отсюда!
# Они должны импортироваться напрямую из src.data

__all__ = [
    # Основные компоненты
    "EntityStore",
    "RelationIndex",
    "ValidityIndex",
    "ParentInfo",
    
    # Утилиты навигации (не константы!)
    "get_child_type",
    "get_parent_type",
    "get_parent_id",
    "get_node_type",
    "get_model_class",
]