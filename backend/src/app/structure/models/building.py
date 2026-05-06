# backend/src/app/structure/models/building.py
"""
Модель Building для таблицы physical.buildings.
"""

from typing import Optional
from sqlmodel import Field
from .base import StructureBase


class Building(StructureBase, table=True):
    """Корпус (в составе комплекса)."""
    
    __tablename__: str = "buildings"  # type: ignore
    __table_args__ = {"schema": "physical"}
    
    complex_id: int = Field(foreign_key="physical.complexes.id", nullable=False)
    name: str = Field(nullable=False)
    address: Optional[str] = Field(default=None)
    floors_count: int = Field(default=0, nullable=False)
    owner_id: Optional[int] = Field(default=None)