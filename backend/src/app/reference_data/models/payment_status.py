# backend/src/app/reference_data/models/payment_status.py
"""
Модель для таблицы payment_statuses (схема dictionary).
"""

from typing import Optional
from sqlmodel import Field
from .base import ReferenceBase


class PaymentStatus(ReferenceBase, table=True):
    """Статус платежа."""
    __tablename__: str = "payment_statuses"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    is_initial: Optional[bool] = Field(default=False)
    is_success: Optional[bool] = Field(default=False)