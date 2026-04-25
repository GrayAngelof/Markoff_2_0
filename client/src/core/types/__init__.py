# client/src/core/types/__init__.py
"""
Публичное API типов ядра.

ЕДИНСТВЕННЫЙ способ импорта типов:
    from src.core.types import NodeType, NodeIdentifier, EventData, CoreError

Также доступны:
    from src.core.types import ROOT_NODE, HasNodeType, IDetailsViewModel
"""

# ===== ИМПОРТЫ =====
from .event_structures import EventData
from .exceptions import CoreError, NotFoundError, ValidationError, SerializationError
from .nodes import NodeIdentifier, NodeType, ROOT_NODE
from .protocols import HasNodeType, IDetailsViewModel


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Базовые структуры событий
    "EventData",
    # Исключения
    "CoreError",
    "NotFoundError",
    "ValidationError",
    "SerializationError",
    # Узлы и идентификаторы
    "NodeIdentifier",
    "NodeType",
    "ROOT_NODE",
    # Протоколы
    "HasNodeType",
    "IDetailsViewModel",
]