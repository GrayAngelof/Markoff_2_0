# backend/src/core/database.py
"""
Настройки подключения к базе данных
Используем SQLModel (который базируется на SQLAlchemy и Pydantic)
Создаем engine и фабрику сессий
"""
from sqlmodel import create_engine, Session
from typing import Generator

from .config import settings

# Создаем engine для подключения к PostgreSQL
# echo=True полезно для разработки - видим все SQL запросы в консоли
# В production нужно отключать
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Логируем SQL запросы (для разработки)
    pool_size=5,  # Количество постоянных подключений
    max_overflow=10,  # Максимальное количество временных подключений
)

def get_session() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных
    Используется в роутерах через Depends()
    
    Гарантирует закрытие сессии после завершения запроса
    """
    with Session(engine) as session:
        yield session