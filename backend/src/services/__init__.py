# backend/src/services/__init__.py
"""
Инициализатор пакета сервисов
Экспортирует сервисы для удобного импорта
"""
from .physical import get_all_complexes

__all__ = ["get_all_complexes"]