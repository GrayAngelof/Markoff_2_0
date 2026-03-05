# backend/src/models/physical/room.py
"""
Модель Room для таблицы physical.rooms
Представляет помещение на этаже
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Room(SQLModel, table=True):
    """
    Модель помещения (таблица physical.rooms)
    
    Связи:
    - belongs_to: Floor (многие к одному)
    - has_many: Zone (один ко многим)
    """
    
    __tablename__ = "rooms"
    __table_args__ = {"schema": "physical"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Внешний ключ к этажу
    floor_id: int = Field(foreign_key="physical.floors.id", nullable=False)
    
    # Основные поля
    number: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    area: Optional[float] = Field(default=None)
    
    # Ссылки на справочники
    physical_type_id: Optional[int] = Field(default=None)
    status_code: Optional[str] = Field(default=None)
    
    # Дополнительные поля
    max_tenants: Optional[int] = Field(default=None)
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    floor: Optional["Floor"] = Relationship(back_populates="rooms")
    zones: List["Zone"] = Relationship(back_populates="room")
    
    class Config:
        from_attributes = True