# client/src/data/__init__.py
"""
Пакет для работы с данными клиента.
Предоставляет граф сущностей и типы узлов.

Обновлён для поддержки:
- Контрагентов (COUNTERPARTY)
- Ответственных лиц (RESPONSIBLE_PERSON)
"""
from src.data.entity_graph import EntityGraph
from src.data.entity_types import (
    NodeType,
    COMPLEX, BUILDING, FLOOR, ROOM,
    COUNTERPARTY, RESPONSIBLE_PERSON,
    MODEL_TO_NODETYPE, NODETYPE_TO_MODEL
)

__all__ = [
    "EntityGraph",
    "NodeType",
    "COMPLEX", "BUILDING", "FLOOR", "ROOM",
    "COUNTERPARTY", "RESPONSIBLE_PERSON",
    "MODEL_TO_NODETYPE",
    "NODETYPE_TO_MODEL",
]