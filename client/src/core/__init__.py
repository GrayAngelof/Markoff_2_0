# client/src/core/__init__.py
"""
Публичное API ядра приложения.

ПРАВИЛО: Этот файл НИЧЕГО не экспортирует.
Импортируйте всё из конкретных модулей:

    from src.core.types import NodeType, NodeIdentifier
    from src.core.event_bus import EventBus
    from src.core.events import NodeSelected, DataLoaded
    from src.core.rules.hierarchy import get_child_type
    from src.core.types.exceptions import NotFoundError
    from src.core.ports.repository import Repository

Никогда не импортируйте из src.core — только из конкретных подмодулей!
"""

# ===== __INIT__ ПУСТ =====
# Ничего не экспортируем для избежания двойных способов импорта