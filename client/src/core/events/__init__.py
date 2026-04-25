# client/src/core/events/__init__.py
"""
Экспорт всех событий ядра приложения.

ЕДИНСТВЕННЫЙ способ импорта событий:
    from src.core.events import NodeSelected, DataLoaded, ChildrenLoaded

Полный список событий:
    - UI: NodeSelected, NodeExpanded, NodeCollapsed, TabChanged
    - Команды: RefreshRequested, ShowDetailsPanel
    - Данные: DataLoaded, DataError, DataInvalidated
    - Детали: ChildrenLoaded, NodeDetailsLoaded
    - Системные: ConnectionChanged
"""

# ===== ИМПОРТЫ =====
from .definitions import (
    # Типы
    DataLoadedKind,
    # UI события (пользовательские действия)
    NodeSelected,
    NodeExpanded,
    NodeCollapsed,
    CollapseAllRequested,
    CurrentSelectionChanged,
    ExpandedNodesChanged,
    TabChanged,
    # Команды (запросы на действие)
    RefreshRequested,
    ShowDetailsPanel,
    # События данных (результаты загрузки)
    DataLoaded,
    DataError,
    DataInvalidated,
    # События деталей (структурированные данные для UI)
    ChildrenLoaded,
    NodeDetailsLoaded,
    # Системные события (инфраструктура)
    ConnectionChanged,
)


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Типы
    "DataLoadedKind",
    # UI события
    "NodeSelected",
    "NodeExpanded",
    "NodeCollapsed",
    "CollapseAllRequested",
    "CurrentSelectionChanged",
    "ExpandedNodesChanged",
    "TabChanged",
    # Команды
    "RefreshRequested",
    "ShowDetailsPanel",
    # События данных
    "DataLoaded",
    "DataError",
    "DataInvalidated",
    # События деталей
    "ChildrenLoaded",
    "NodeDetailsLoaded",
    # Системные события
    "ConnectionChanged",
]