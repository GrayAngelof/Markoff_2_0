# backend/src/models/dictionary/responsible_person.py
"""
Модель ResponsiblePerson для таблицы dictionary.responsible_persons
"""
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON
from typing import Optional, List
from datetime import datetime

class ResponsiblePerson(SQLModel, table=True):
    """
    Модель ответственного лица
    """
    
    __tablename__ = "responsible_persons"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    counterparty_id: int = Field(foreign_key="dictionary.counterparties.id", nullable=False)
    person_name: str = Field(nullable=False)
    position: Optional[str] = Field(default=None)
    role_code: Optional[str] = Field(default=None, foreign_key="dictionary.role_catalog.code")
    phone: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    contact_categories: Optional[List[str]] = Field(default=None, sa_type=JSON)
    is_public_contact: bool = Field(default=False)
    is_active: bool = Field(default=True)
    hire_date: Optional[datetime] = Field(default=None)
    termination_date: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        from_attributes = True