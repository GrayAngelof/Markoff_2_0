# backend/src/models/dictionary/responsible_person.py
"""
Модель ResponsiblePerson для таблицы dictionary.responsible_persons
Представляет ответственное лицо контрагента
"""
from __future__ import annotations  # <-- ДОБАВЛЕНО

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import JSON

if TYPE_CHECKING:
    from .counterparty import Counterparty
    from .role_catalog import RoleCatalog

class ResponsiblePerson(SQLModel, table=True):
    """
    Модель ответственного лица (таблица dictionary.responsible_persons)
    
    Связи:
    - belongs_to: Counterparty (многие к одному)
    - belongs_to: RoleCatalog (по role_code)
    """
    
    __tablename__ = "responsible_persons"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Внешний ключ к контрагенту
    counterparty_id: int = Field(foreign_key="dictionary.counterparties.id", nullable=False)
    
    # Основные поля
    person_name: str = Field(nullable=False)
    position: Optional[str] = Field(default=None)
    role_code: Optional[str] = Field(default=None, foreign_key="dictionary.role_catalog.code")
    
    # Контакты
    phone: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    
    # Категории контактов (массив)
    contact_categories: Optional[List[str]] = Field(default=None, sa_type=JSON)
    
    # Флаги
    is_public_contact: bool = Field(default=False)
    is_active: bool = Field(default=True)
    
    # Даты
    hire_date: Optional[datetime] = Field(default=None)
    termination_date: Optional[datetime] = Field(default=None)
    
    # Метаданные
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    counterparty: Optional["Counterparty"] = Relationship(back_populates="responsible_persons")
    role: Optional["RoleCatalog"] = Relationship(back_populates="responsible_persons")
    
    class Config:
        from_attributes = True