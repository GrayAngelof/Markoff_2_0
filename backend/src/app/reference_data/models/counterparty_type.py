# backend/src/app/reference_data/models/counterparty_type.py
"""
Модель для таблицы counterparty_types (схема dictionary).
"""

from typing import Optional
from sqlmodel import Field
from .base import ReferenceBase


class CounterpartyType(ReferenceBase, table=True):
    """Тип контрагента."""
    __tablename__: str = "counterparty_types"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    is_active: Optional[bool] = Field(default=True)