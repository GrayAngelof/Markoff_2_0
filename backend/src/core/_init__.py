# backend/src/core/__init__.py
"""
Инициализатор пакета core
Экспортирует основные компоненты ядра приложения
"""
from .config import settings
from .deps import get_db, engine

__all__ = [
    "settings",
    "get_db",
    "engine"
]