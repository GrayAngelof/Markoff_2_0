# client/src/core/__init__.py
"""
Публичное API ядра приложения.

Экспортируем только самые базовые типы и классы.
Всё остальное импортируется из соответствующих подмодулей:

    from core.types import NodeType, NodeIdentifier
    from core.events import NodeSelected, DataLoaded
    from core.hierarchy import get_child_type
    from core.serializers import identifier_to_key
    from core.exceptions import NotFoundError, SerializationError
    from core.interfaces import Repository
"""
from .types import NodeType, NodeIdentifier
from .event_bus import EventBus
from .types.exceptions import CoreError, NotFoundError, ValidationError

__all__ = [
    # Базовые типы
    "NodeType",
    "NodeIdentifier",
    
    # Шина событий
    "EventBus",
    
    # Базовые исключения
    "CoreError",
    "NotFoundError",
    "ValidationError",
]