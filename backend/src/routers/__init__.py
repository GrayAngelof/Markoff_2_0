# backend/src/routers/__init__.py
"""
Инициализатор пакета роутеров
Экспортирует все роутеры для подключения в main.py
"""
from .physical import router as physical_router

__all__ = ["physical_router"]