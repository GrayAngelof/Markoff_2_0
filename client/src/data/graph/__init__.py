# client/src/data/graph/__init__.py
"""
Пакет компонентов графа сущностей.

Предоставляет модульную структуру для работы с данными.
"""
from src.data.graph.entity_store import EntityStore
from src.data.graph.relation_index import RelationIndex, ParentInfo
from src.data.graph.validity_index import ValidityIndex
from src.data.graph.schema import (
    get_child_type,
    get_parent_type,
    get_parent_id,
    get_node_type,
    get_model_class
)

__all__ = [
    "EntityStore",
    "RelationIndex",
    "ValidityIndex",
    "ParentInfo",
    "get_child_type",
    "get_parent_type",
    "get_parent_id",
    "get_node_type",
    "get_model_class",
]