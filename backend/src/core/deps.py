# backend/src/core/deps.py
"""
Общие зависимости для всего приложения
Сейчас содержит только get_db, но в будущем расширится
(авторизация, текущий пользователь, etc.)
"""
from typing import Generator
from sqlmodel import Session

from .database import engine

def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии БД
    Используется во всех роутерах, которым нужен доступ к базе
    
    Пример использования в эндпоинте:
    @router.get("/")
    def get_items(db: Session = Depends(get_db)):
        ...
    """
    with Session(engine) as session:
        yield session