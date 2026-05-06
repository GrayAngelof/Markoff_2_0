# backend/src/app/structure/models/floor.py
"""
Модель Floor для таблицы physical.floors.
"""

from typing import Optional
from sqlmodel import Field
from .base import StructureBase


class Floor(StructureBase, table=True):
    """Этаж (в составе корпуса)."""
    
    __tablename__: str = "floors"  # type: ignore
    __table_args__ = {"schema": "physical"}
    
    building_id: int = Field(foreign_key="physical.buildings.id", nullable=False)
    number: int = Field(nullable=False)
    physical_type_id: Optional[int] = Field(default=None)
    plan_image_url: Optional[str] = Field(default=None)