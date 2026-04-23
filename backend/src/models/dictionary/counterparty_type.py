# backend/src/models/dictionary/counterparty_type.py
"""
Модель CounterpartyType для таблицы dictionary.counterparty_types
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class CounterpartyType(SQLModel, table=True):
    """
    Модель типа контрагента
    """
    
    __tablename__ = "counterparty_types"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(nullable=False, unique=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        from_attributes = True