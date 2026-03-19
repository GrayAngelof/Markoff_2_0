# client/src/core/__init__.py
"""
Публичное API ядра приложения.
"""
from .types import NodeType, NodeIdentifier
from .event_bus import EventBus
from .event_constants import (
    UIEvents, SystemEvents, HotkeyEvents,
    ProjectionEvents, CustomEvents
)
from .types.exceptions import CoreError, ValidationError

# Новый экспорт
from .interfaces import Repository

__all__ = [
    "NodeType",
    "NodeIdentifier",
    "EventBus",
    "UIEvents",
    "SystemEvents",
    "HotkeyEvents",
    "ProjectionEvents",
    "CustomEvents",
    "CoreError",
    "ValidationError",
    "Repository",  # ← добавить
]