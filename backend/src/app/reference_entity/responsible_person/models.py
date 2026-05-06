# backend/src/app/reference_entity/responsible_person/models.py
"""
Модель для таблицы responsible_persons (схема dictionary).

Сущность "ответственное лицо" — связана с контрагентом.
"""

from datetime import datetime, date, timezone
from typing import Optional, List
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ARRAY, String


def utc_now() -> datetime:
    """Возвращает текущее время в UTC с timezone-информацией."""
    return datetime.now(timezone.utc)


class ResponsiblePerson(SQLModel, table=True):
    """Ответственное лицо контрагента."""
    
    __tablename__: str = "responsible_persons"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    counterparty_id: int = Field(foreign_key="dictionary.counterparties.id", nullable=False)
    person_name: str = Field(max_length=255, nullable=False)
    position: Optional[str] = Field(default=None, max_length=255)
    department: Optional[str] = Field(default=None, max_length=255)
    role_code: Optional[str] = Field(default=None, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    contact_categories: Optional[List[str]] = Field(
        default=None, 
        sa_column=Column(ARRAY(String))
    )
    is_public_contact: bool = Field(default=False)
    is_active: bool = Field(default=True)
    hire_date: Optional[date] = Field(default=None)
    termination_date: Optional[date] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)