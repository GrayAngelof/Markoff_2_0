# backend/src/app/reference_data/models/room_status.py
"""
Модель для таблицы room_statuses (схема dictionary).
"""

from typing import Optional
from sqlmodel import Field
from .base import ReferenceBase


class RoomStatus(ReferenceBase, table=True):
    """Статус помещения."""
    __tablename__: str = "room_statuses"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    is_initial: Optional[bool] = Field(default=False)
    allows_rent: Optional[bool] = Field(default=False)