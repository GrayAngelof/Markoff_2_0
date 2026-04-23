# backend/src/core/deps.py
"""
Зависимости для FastAPI.

Содержит DI-зависимости: получение сессии БД, аутентификация и т.д.
"""

# ===== ИМПОРТЫ =====
from typing import Generator

from sqlmodel import Session, create_engine

from .config import settings


# ===== КОНСТАНТЫ =====
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


# ===== ФУНКЦИИ =====
def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных.

    Yields:
        Сессия SQLModel
    """
    with Session(engine) as session:
        yield session