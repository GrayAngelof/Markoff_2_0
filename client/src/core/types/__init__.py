# client/src/core/types/__init__.py
"""
Публичное API типов ядра.

Экспортируем только самые базовые типы.
Остальное импортируется из соответствующих подмодулей:

    from src.core.types.nodes import NodeType, NodeIdentifier
    from src.core.types.event_structures import EventData
    from src.core.types.exceptions import NotFoundError, SerializationError
"""

# ===== ИМПОРТЫ =====
from .event_structures import EventData
from .exceptions import CoreError, NotFoundError, ValidationError
from .nodes import NodeIdentifier, NodeType, ROOT_NODE
from .protocols import HasNodeType, IDetailsViewModel


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Базовые типы (нужны везде)
    "NodeType",
    "NodeIdentifier",
    "ROOT_NODE",
    # Структуры событий
    "EventData",
    # Базовые исключения
    "CoreError",
    "NotFoundError",
    "ValidationError",
    # Протоколы
    "HasNodeType",
    "IDetailsViewModel",
]