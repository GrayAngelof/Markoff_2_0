"""
Публичное API ядра приложения.

Экспортируем только самые базовые типы и классы.
Всё остальное импортируется из соответствующих подмодулей:

    from src.core.types import NodeType, NodeIdentifier
    from src.core.events import NodeSelected, NodeExpanded, NodeCollapsed, TabChanged
    from src.core.rules.hierarchy import get_child_type
    from src.core.types.exceptions import NotFoundError, SerializationError
    from src.core.ports.repository import Repository

Список событий:
    - NodeSelected, NodeExpanded, NodeCollapsed, TabChanged
    - RefreshRequested, ShowDetailsPanel
    - DataLoaded, DataError, DataInvalidated
    - ChildrenLoaded, NodeDetailsLoaded
    - ConnectionChanged
"""

# Базовые типы
from .types import NodeType, NodeIdentifier

# Шина событий (фасад)
from .event_bus import EventBus

# Исключения
from .types.exceptions import CoreError, NotFoundError, ValidationError

# Интерфейсы (ports)
from .ports.repository import Repository

# События
from .events import (
    NodeSelected,
    NodeExpanded,
    NodeCollapsed,
    TabChanged,
    RefreshRequested,
    ShowDetailsPanel,
    DataLoaded,
    DataError,
    DataInvalidated,
    ChildrenLoaded,
    NodeDetailsLoaded,
    ConnectionChanged,
)

__all__ = [
    # Базовые типы
    "NodeType",
    "NodeIdentifier",
    
    # Шина событий
    "EventBus",
    
    # Исключения
    "CoreError",
    "NotFoundError",
    "ValidationError",
    
    # Интерфейсы
    "Repository",
    
    # События
    "NodeSelected",
    "NodeExpanded",
    "NodeCollapsed",
    "TabChanged",
    "RefreshRequested",
    "ShowDetailsPanel",
    "DataLoaded",
    "DataError",
    "DataInvalidated",
    "ChildrenLoaded",
    "NodeDetailsLoaded",
    "ConnectionChanged",
]