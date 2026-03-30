"""
Публичное API типов ядра.

Экспортируем только самые базовые типы.
Остальное импортируется из соответствующих подмодулей:

    from src.core.types.nodes import NodeType, NodeIdentifier
    from src.core.types.event_structures import EventData
    from src.core.types.exceptions import NotFoundError, SerializationError
"""
from .nodes import NodeType, NodeIdentifier
from .event_structures import EventData
from .exceptions import CoreError, NotFoundError, ValidationError

__all__ = [
    # Базовые типы (нужны везде)
    "NodeType",
    "NodeIdentifier",
    
    # Структуры событий
    "EventData",
    
    # Базовые исключения
    "CoreError",
    "NotFoundError",
    "ValidationError",
]