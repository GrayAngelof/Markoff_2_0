# backend/src/services/__init__.py
"""
Инициализатор пакета сервисов.

Экспортирует сервисы для работы с данными:
- PhysicalService — сервис для физической структуры (комплексы, здания, этажи, помещения)
- DictionaryService — сервис для справочных данных (статусы, типы)
"""

# ===== ИМПОРТЫ =====
from .dictionary_service import DictionaryService
from .physical_service import PhysicalService


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    "DictionaryService",
    "PhysicalService",
]