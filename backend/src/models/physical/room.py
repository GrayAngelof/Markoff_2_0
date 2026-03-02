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
    number: str = Field(nullable=False)  # Номер помещения (строка, может быть "101А")
    description: Optional[str] = Field(default=None)
    area: Optional[float] = Field(default=None)  # Площадь в кв. метрах
    
    # Ссылки на справочники
    physical_type_id: int = Field(nullable=False)  # Тип помещения (офис, склад и т.д.)
    status_code: str = Field(nullable=False)  # Статус (свободно, занято и т.д.)
    
    # Дополнительные поля
    max_tenants: Optional[int] = Field(default=None)  # Макс. количество арендаторов
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    floor: Optional["Floor"] = Relationship(back_populates="rooms")
    zones: List["Zone"] = Relationship(back_populates="room")
    
    class Config:
        from_attributes = True