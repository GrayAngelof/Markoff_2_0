# client/src/core/__init__.py
"""
Публичное API ядра приложения.

Экспортируем только самые базовые типы и классы.
Всё остальное импортируется из соответствующих подмодулей:

    from src.core.types import NodeType, NodeIdentifier
    from src.core.events import NodeSelected, DataLoaded
    from src.core.hierarchy import get_child_type
    from src.core.serializers import identifier_to_key
    from src.core.exceptions import NotFoundError, SerializationError
    from src.core.interfaces import Repository
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