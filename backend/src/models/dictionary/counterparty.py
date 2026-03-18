# backend/src/models/dictionary/counterparty.py
"""
Модель Counterparty для таблицы dictionary.counterparties
"""
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON
from typing import Optional
from datetime import datetime

class Counterparty(SQLModel, table=True):
    """
    Модель контрагента
    """
    
    __tablename__ = "counterparties"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    type_id: Optional[int] = Field(default=None, foreign_key="dictionary.counterparty_types.id")
    short_name: str = Field(nullable=False)
    full_name: Optional[str] = Field(default=None)
    tax_id: Optional[str] = Field(default=None)
    legal_address: Optional[str] = Field(default=None)
    actual_address: Optional[str] = Field(default=None)
    bank_details: Optional[dict] = Field(default=None, sa_type=JSON)
    status_code: str = Field(default="active", foreign_key="dictionary.counterparty_statuses.code")
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        from_attributes = True