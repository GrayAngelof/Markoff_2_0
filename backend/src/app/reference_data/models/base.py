# backend/src/app/reference_data/models/base.py
"""
Базовый класс для всех справочников (reference data).
"""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Возвращает текущее время в UTC с timezone-информацией."""
    return datetime.now(timezone.utc)


class ReferenceBase(SQLModel):
    """
    Абстрактная база для всех справочников.
    Содержит общие поля.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(max_length=50, unique=True, nullable=False)
    name: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    display_order: int = Field(default=0)
    created_at: Optional[datetime] = Field(default_factory=utc_now)
    updated_at: Optional[datetime] = Field(default_factory=utc_now)

    class Config:
        arbitrary_types_allowed = True