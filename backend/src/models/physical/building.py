# backend/src/models/physical/building.py
"""
Модель Building для таблицы physical.buildings
Представляет корпус в составе комплекса
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Building(SQLModel, table=True):
    """
    Модель корпуса (таблица physical.buildings)
    
    Связи:
    - belongs_to: Complex (многие к одному)
    - has_many: Floor (один ко многим)
    """
    
    __tablename__ = "buildings"
    __table_args__ = {"schema": "physical"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Внешний ключ к комплексу
    complex_id: int = Field(foreign_key="physical.complexes.id", nullable=False)
    
    # Основные поля
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)  # Добавлено поле address
    floors_count: int = Field(nullable=False)
    
    # Статус
    status_id: int = Field(nullable=False)
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    complex: Optional["Complex"] = Relationship(back_populates="buildings")
    floors: List["Floor"] = Relationship(back_populates="building")
    
    class Config:
        from_attributes = True