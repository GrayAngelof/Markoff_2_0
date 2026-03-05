# backend/src/models/physical/floor.py
"""
Модель Floor для таблицы physical.floors
Представляет этаж в корпусе
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Floor(SQLModel, table=True):
    """
    Модель этажа (таблица physical.floors)
    
    Связи:
    - belongs_to: Building (многие к одному)
    - has_many: Room (один ко многим)
    """
    
    __tablename__ = "floors"
    __table_args__ = {"schema": "physical"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Внешний ключ к корпусу
    building_id: int = Field(foreign_key="physical.buildings.id", nullable=False)
    
    # Основные поля
    number: int = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    
    # Ссылки на справочники
    physical_type_id: Optional[int] = Field(default=None)
    status_id: Optional[int] = Field(default=None)
    
    # URL к плану этажа
    plan_image_url: Optional[str] = Field(default=None)
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    building: Optional["Building"] = Relationship(back_populates="floors")
    rooms: List["Room"] = Relationship(back_populates="floor")
    
    class Config:
        from_attributes = True