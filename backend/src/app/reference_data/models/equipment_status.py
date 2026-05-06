# backend/src/app/reference_data/models/equipment_status.py
"""
Модель для таблицы equipment_statuses (схема dictionary).
"""

from typing import Optional
from sqlmodel import Field
from .base import ReferenceBase


class EquipmentStatus(ReferenceBase, table=True):
    """Статус оборудования."""
    __tablename__: str = "equipment_statuses"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    is_initial: Optional[bool] = Field(default=False)
    is_operational: Optional[bool] = Field(default=True)