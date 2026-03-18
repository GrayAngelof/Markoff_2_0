# backend/src/models/physical/complex.py
"""
Модель Complex для таблицы physical.complexes
Простая модель без отношений - только данные
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Complex(SQLModel, table=True):
    """
    Модель комплекса (таблица physical.complexes)
    """
    
    __tablename__ = "complexes"  # type: ignore
    __table_args__ = {"schema": "physical"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)
    description: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    owner_id: Optional[int] = Field(default=None, foreign_key="dictionary.counterparties.id")
    status_id: int = Field(nullable=False, foreign_key="dictionary.building_statuses.id")
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        from_attributes = True