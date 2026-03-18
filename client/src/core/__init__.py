# client/src/core/__init__.py
"""
Публичное API ядра приложения.

Этот модуль экспортирует только то, что нужно внешнему миру:
- EventBus - главный фасад для работы с событиями
- Все константы событий из events.py

Все внутренние детали реализации скрыты в пакете .bus/
Внешний код никогда не должен импортировать из core.bus напрямую!

Пример использования:
    from src.core import EventBus, UIEvents
    
    bus = EventBus()
    bus.subscribe(UIEvents.NODE_SELECTED, my_handler)
    bus.emit(UIEvents.NODE_SELECTED, {'node_id': 42})
"""

from .event_bus import EventBus
from .events import (
    UIEvents, SystemEvents, HotkeyEvents, ProjectionEvents, ALL_EVENTS
)

__all__ = [
    'EventBus',
    'UIEvents',
    'SystemEvents',
    'HotkeyEvents',
    'ProjectionEvents',
    'ALL_EVENTS',
]