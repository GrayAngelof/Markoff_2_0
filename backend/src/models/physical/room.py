# backend/src/models/physical/room.py
"""
Модель Room для таблицы physical.rooms
Простая модель без отношений
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Room(SQLModel, table=True):
    """
    Модель помещения (таблица physical.rooms)
    """
    
    __tablename__ = "rooms"  # type: ignore
    __table_args__ = {"schema": "physical"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    floor_id: int = Field(foreign_key="physical.floors.id", nullable=False)
    number: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    area: Optional[float] = Field(default=None)
    physical_type_id: Optional[int] = Field(default=None, foreign_key="dictionary.physical_room_types.id")
    status_id: Optional[int] = Field(default=None, foreign_key="dictionary.room_statuses.id")
    max_tenants: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        from_attributes = True