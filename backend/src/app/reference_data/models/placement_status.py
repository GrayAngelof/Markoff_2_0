# backend/src/app/reference_data/models/placement_status.py
"""
Модель для таблицы placement_statuses (схема dictionary).
"""

from typing import Optional
from sqlmodel import Field
from .base import ReferenceBase


class PlacementStatus(ReferenceBase, table=True):
    """Статус размещения."""
    __tablename__: str = "placement_statuses"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    is_initial: Optional[bool] = Field(default=False)