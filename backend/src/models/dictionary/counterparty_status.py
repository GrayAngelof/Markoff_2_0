# backend/src/models/dictionary/counterparty_status.py
"""
Модель CounterpartyStatus для таблицы dictionary.counterparty_statuses
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class CounterpartyStatus(SQLModel, table=True):
    """
    Модель статуса контрагента
    """
    
    __tablename__ = "counterparty_statuses"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(nullable=False, unique=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    is_initial: bool = Field(default=False)
    display_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        from_attributes = True