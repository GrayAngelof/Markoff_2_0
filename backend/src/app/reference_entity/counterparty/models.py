# backend/src/app/reference_entity/counterparty/models.py
"""
Модель для таблицы counterparties (схема dictionary).

Сущность "контрагент" — загружается по ID (lazy loading).
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON


def utc_now() -> datetime:
    """Возвращает текущее время в UTC с timezone-информацией."""
    return datetime.now(timezone.utc)


class Counterparty(SQLModel, table=True):
    """Контрагент (юридическое или физическое лицо)."""
    
    __tablename__: str = "counterparties"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    short_name: str = Field(max_length=255, nullable=False)
    full_name: str = Field(max_length=500, nullable=False)
    tax_id: Optional[str] = Field(default=None, max_length=50, description="ИНН")
    legal_address: Optional[str] = Field(default=None)
    actual_address: Optional[str] = Field(default=None)
    bank_details: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    status_code: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None)
    type_id: Optional[int] = Field(default=None)  # foreign key к counterparty_types
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)