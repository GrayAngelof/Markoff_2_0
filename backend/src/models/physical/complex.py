# backend/src/models/physical/complex.py
"""
Модель Complex для таблицы physical.complexes
Представляет комплекс зданий
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Complex(SQLModel, table=True):
    """
    Модель комплекса (таблица physical.complexes)
    
    Связи:
    - has_many: Building (один ко многим)
    """
    
    __tablename__ = "complexes"
    __table_args__ = {"schema": "physical"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Основные поля
    name: str = Field(nullable=False, unique=True)
    description: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    
    # Денормализованные поля для быстрого доступа
    # buildings_count: int = Field(nullable=False, default=0)
    
    # Статус
    status_id: int = Field(nullable=False)
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    buildings: List["Building"] = Relationship(back_populates="complex")
    
    class Config:
        from_attributes = True