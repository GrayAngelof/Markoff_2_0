# backend/src/models/physical/complex.py
"""
Модель Complex для таблицы physical.complexes
Представляет комплекс зданий
"""
from __future__ import annotations  # <-- ДОБАВЛЕНО

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .building import Building
    from ..dictionary.counterparty import Counterparty

class Complex(SQLModel, table=True):
    """
    Модель комплекса (таблица physical.complexes)
    
    Связи:
    - belongs_to: Counterparty (как владелец)
    - has_many: Building (один ко многим)
    """
    
    __tablename__ = "complexes"  # type: ignore
    __table_args__ = {"schema": "physical"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Основные поля
    name: str = Field(nullable=False, unique=True)
    description: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    
    # Владелец (ссылка на dictionary.counterparties)
    owner_id: Optional[int] = Field(default=None, foreign_key="dictionary.counterparties.id")
    
    # Статус
    status_id: int = Field(nullable=False)
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    buildings: List["Building"] = Relationship(back_populates="complex")
    owner: Optional["Counterparty"] = Relationship(back_populates="complexes")
    
    class Config:
        from_attributes = True