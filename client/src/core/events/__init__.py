# client/src/core/events/__init__.py
"""
Экспорт всех событий ядра приложения.

Позволяет делать:
    from src.core.events import NodeSelected, DataLoaded
"""

from .definitions import (
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