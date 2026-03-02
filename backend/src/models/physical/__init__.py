# backend/src/models/physical/__init__.py
"""
Инициализатор пакета моделей схемы physical
Экспортирует все модели для удобного импорта

Пример использования:
from src.models.physical import Complex
"""
from .complex import Complex

__all__ = ["Complex"]