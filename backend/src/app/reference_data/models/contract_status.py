# backend/src/app/reference_data/models/contract_status.py
"""
Модель для таблицы contract_statuses (схема dictionary).
"""

from typing import Optional
from sqlmodel import Field
from .base import ReferenceBase


class ContractStatus(ReferenceBase, table=True):
    """Статус договора."""
    __tablename__: str = "contract_statuses"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    is_initial: Optional[bool] = Field(default=False)
    is_terminal: Optional[bool] = Field(default=False)