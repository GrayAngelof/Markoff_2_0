# backend/src/app/structure/models/room.py
"""
Модель Room для таблицы physical.rooms.
"""

from typing import Optional
from sqlmodel import Field
from .base import StructureBase


class Room(StructureBase, table=True):
    """Помещение (на этаже)."""
    
    __tablename__: str = "rooms"  # type: ignore
    __table_args__ = {"schema": "physical"}
    
    floor_id: int = Field(foreign_key="physical.floors.id", nullable=False)
    number: str = Field(nullable=False)
    area: Optional[float] = Field(default=None)
    physical_type_id: Optional[int] = Field(default=None)
    max_tenants: Optional[int] = Field(default=None)