# backend/src/app/structure/models/base.py
"""
Базовая модель для физической иерархии (structure).
"""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Возвращает текущее время в UTC с timezone-информацией."""
    return datetime.now(timezone.utc)


class StructureBase(SQLModel):
    """
    Абстрактная база для всех моделей физической иерархии.
    
    Содержит общие поля:
    - id: первичный ключ
    - description: описание
    - status_id: идентификатор статуса (справочник)
    - created_at, updated_at: временные метки
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    description: Optional[str] = Field(default=None)
    status_id: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Config:
        arbitrary_types_allowed = True