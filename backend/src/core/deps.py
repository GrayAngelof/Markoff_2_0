# backend/src/core/deps.py
"""
Зависимости для FastAPI
"""
from sqlmodel import Session, create_engine
from typing import Generator

from .config import settings

# Создаем engine для подключения к БД
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии БД
    
    Yields:
        Session: Сессия SQLModel
    """
    with Session(engine) as session:
        yield session