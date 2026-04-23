# backend/src/routers/__init__.py
"""
Инициализатор пакета роутеров.

Экспортирует все роутеры для подключения в main.py:
- physical_router — роутер для физической структуры (комплексы, здания, этажи, помещения)
- dictionary_router — роутер для справочных данных (статусы, типы)
"""

# ===== ИМПОРТЫ =====
from .dictionary import router as dictionary_router
from .physical import router as physical_router


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    "dictionary_router",
    "physical_router",
]