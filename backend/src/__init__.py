# backend/src/__init__.py
"""
Инициализатор пакета src для бэкенда Markoff
Экспортирует основные компоненты для удобного импорта
"""
from .main import app

__all__ = ["app"]