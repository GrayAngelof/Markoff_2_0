# backend/src/core/__init__.py
"""
Инициализатор пакета core.

Экспортирует основные компоненты ядра приложения:
- settings — конфигурация приложения
- get_db — зависимость для получения сессии БД
- engine — движок SQLAlchemy
"""

# ===== ИМПОРТЫ =====
from .config import settings
from .deps import engine, get_db


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    "engine",
    "get_db",
    "settings",
]