# backend/src/models/physical/zone.py
"""
Модель Zone для таблицы physical.zones
Представляет зону внутри помещения (для детальной планировки)
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON  # Добавляем импорт JSON из SQLAlchemy
from typing import Optional, Any
from datetime import datetime

class Zone(SQLModel, table=True):
    """
    Модель зоны (таблица physical.zones)
    
    Используется для детальной разметки помещений:
    - Размещение датчиков
    - Планировка рабочих мест
    - Зоны ответственности
    """
    
    __tablename__ = "zones"
    __table_args__ = {"schema": "physical"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Внешний ключ к помещению
    room_id: int = Field(foreign_key="physical.rooms.id", nullable=False)
    
    # Основные поля
    name: str = Field(nullable=False)  # Название зоны (например, "Зона А", "Стойка 1")
    description: Optional[str] = Field(default=None)
    
    # Координаты полигона на плане (JSON формат)
    # Используем sa_type=JSON для указания типа колонки в БД
    polygon_coordinates: Optional[Any] = Field(default=None, sa_type=JSON)
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    room: Optional["Room"] = Relationship(back_populates="zones")
    
    class Config:
        from_attributes = True
        # Для работы с JSON полем
        arbitrary_types_allowed = True