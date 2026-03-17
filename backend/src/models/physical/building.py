# backend/src/models/physical/building.py
"""
Модель Building для таблицы physical.buildings
Представляет корпус в составе комплекса
"""
from __future__ import annotations  # <-- ДОБАВЛЕНО

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .complex import Complex
    from .floor import Floor
    from ..dictionary.counterparty import Counterparty

class Building(SQLModel, table=True):
    """
    Модель корпуса (таблица physical.buildings)
    
    Связи:
    - belongs_to: Complex (многие к одному)
    - belongs_to: Counterparty (как владелец)
    - has_many: Floor (один ко многим)
    """
    
    __tablename__ = "buildings"  # type: ignore
    __table_args__ = {"schema": "physical"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Внешний ключ к комплексу
    complex_id: int = Field(foreign_key="physical.complexes.id", nullable=False)
    
    # Основные поля
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    floors_count: int = Field(nullable=False)
    
    # Владелец (ссылка на dictionary.counterparties)
    owner_id: Optional[int] = Field(default=None, foreign_key="dictionary.counterparties.id")
    
    # Статус
    status_id: int = Field(nullable=False)
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    complex: Optional["Complex"] = Relationship(back_populates="buildings")
    owner: Optional["Counterparty"] = Relationship(back_populates="buildings")
    floors: List["Floor"] = Relationship(back_populates="building")
    
    class Config:
        from_attributes = True