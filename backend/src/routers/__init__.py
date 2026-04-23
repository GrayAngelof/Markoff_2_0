# backend/src/routers/__init__.py
"""
Инициализатор пакета роутеров
Экспортирует все роутеры для подключения в main.py
"""
from .physical import router as physical_router
from .dictionary import router as dictionary_router

__all__ = ["physical_router", "dictionary_router"]