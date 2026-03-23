# client/src/core/types/__init__.py
"""
Публичное API типов ядра.

Экспортируем только самые базовые типы.
Остальное импортируется из соответствующих подмодулей:

    from core.types.nodes import NodeType, NodeIdentifier
    from core.types.event_structures import EventData, Event
    from core.types.exceptions import NotFoundError, SerializationError
"""
from .nodes import NodeType, NodeIdentifier
from .event_structures import EventData, Event
from .exceptions import CoreError, NotFoundError, ValidationError

__all__ = [
    # Базовые типы (нужны везде)
    "NodeType",
    "NodeIdentifier",
    
    # Структуры событий
    "EventData",
    "Event",
    
    # Базовые исключения
    "CoreError",
    "NotFoundError",
    "ValidationError",
]