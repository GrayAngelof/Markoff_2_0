# backend/src/services/__init__.py
"""
Инициализатор пакета сервисов
"""
from .physical_service import PhysicalService
from .dictionary_service import DictionaryService

__all__ = ["PhysicalService", "DictionaryService"]