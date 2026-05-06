# backend/src/app/reference_data/models/building_status.py
"""
Модель для таблицы building_statuses (схема dictionary).
"""

from typing import Optional
from sqlmodel import Field
from .base import ReferenceBase


class BuildingStatus(ReferenceBase, table=True):
    """Статус здания."""
    __tablename__: str = "building_statuses"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    is_initial: Optional[bool] = Field(default=False)
    allows_occupancy: Optional[bool] = Field(default=False)