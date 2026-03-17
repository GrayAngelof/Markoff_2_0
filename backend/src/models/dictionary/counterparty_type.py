# backend/src/models/dictionary/counterparty_type.py
"""
Модель CounterpartyType для таблицы dictionary.counterparty_types
Представляет тип контрагента (собственник, арендатор, поставщик и т.д.)
"""
from __future__ import annotations  # <-- ДОБАВЛЕНО

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .counterparty import Counterparty

class CounterpartyType(SQLModel, table=True):
    """
    Модель типа контрагента (таблица dictionary.counterparty_types)
    
    Связи:
    - has_many: Counterparty (один ко многим)
    """
    
    __tablename__ = "counterparty_types"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Код типа (landlord_owner, tenant_commercial, supplier_utilities и т.д.)
    code: str = Field(nullable=False, unique=True)
    
    # Название для отображения
    name: str = Field(nullable=False)
    
    # Описание
    description: Optional[str] = Field(default=None)
    
    # Порядок отображения
    display_order: int = Field(default=0)
    
    # Активен ли тип
    is_active: bool = Field(default=True)
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    counterparties: List["Counterparty"] = Relationship(back_populates="type")
    
    class Config:
        from_attributes = True