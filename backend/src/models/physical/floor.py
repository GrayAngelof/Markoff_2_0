# backend/src/models/physical/floor.py
"""
Модель Floor для таблицы physical.floors
Простая модель без отношений
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Floor(SQLModel, table=True):
    """
    Модель этажа (таблица physical.floors)
    """
    
    __tablename__ = "floors"  # type: ignore
    __table_args__ = {"schema": "physical"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    building_id: int = Field(foreign_key="physical.buildings.id", nullable=False)
    number: int = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    physical_type_id: Optional[int] = Field(default=None, foreign_key="dictionary.physical_room_types.id")
    status_id: Optional[int] = Field(default=None, foreign_key="dictionary.building_statuses.id")
    plan_image_url: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        from_attributes = True