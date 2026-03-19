# client/src/core/types/__init__.py
"""
Публичное API типов ядра.

Экспортирует все типы, которые нужны внешнему миру.
Внутренняя структура пакета скрыта.
"""
from .nodes import (
    NodeType, NodeID, NodeKey, ParentInfo, NodeIdentifier
)
from .event_structures import (
    EventData, Event
)
from .exceptions import (
    CoreError, ConfigurationError, HierarchyError,
    SerializationError, ValidationError, NotFoundError,
    DuplicateError
)

__all__ = [
    # Типы узлов
    'NodeType',
    'NodeID',
    'NodeKey',
    'ParentInfo',
    'NodeIdentifier',
    
    # Структуры событий
    'EventData',
    'Event',
    
    # Исключения
    'CoreError',
    'ConfigurationError',
    'HierarchyError',
    'SerializationError',
    'ValidationError',
    'NotFoundError',
    'DuplicateError',
]