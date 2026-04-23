# backend/src/core/database.py
"""
Настройки подключения к базе данных.

Использует SQLModel (на базе SQLAlchemy и Pydantic)
для создания engine и фабрики сессий.
"""

# ===== ИМПОРТЫ =====
from typing import Generator

from sqlmodel import Session, create_engine

from .config import settings


# ===== КОНСТАНТЫ =====
# Создаём engine для подключения к PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,        # Логируем SQL запросы (для разработки)
    pool_size=5,      # Количество постоянных подключений
    max_overflow=10,  # Максимальное количество временных подключений
)


# ===== ФУНКЦИИ =====
def get_session() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных.

    Используется в роутерах через Depends().
    Гарантирует закрытие сессии после завершения запроса.
    """
    with Session(engine) as session:
        yield session