# backend/src/models/physical/zone.py
"""
Модель Zone для таблицы physical.zones
Простая модель без отношений
"""
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON
from typing import Optional, Any
from datetime import datetime

class Zone(SQLModel, table=True):
    """
    Модель зоны (таблица physical.zones)
    """
    
    __tablename__ = "zones"  # type: ignore
    __table_args__ = {"schema": "physical"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="physical.rooms.id", nullable=False)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    polygon_coordinates: Optional[Any] = Field(default=None, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True