# backend/src/models/dictionary/role_catalog.py
"""
Модель RoleCatalog для таблицы dictionary.role_catalog
Представляет роли ответственных лиц
"""
from __future__ import annotations  # <-- ДОБАВЛЕНО

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .responsible_person import ResponsiblePerson

class RoleCatalog(SQLModel, table=True):
    """
    Модель роли (таблица dictionary.role_catalog)
    
    Связи:
    - has_many: ResponsiblePerson (один ко многим)
    """
    
    __tablename__ = "role_catalog"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Код роли (general_director, chief_accountant, contact_person и т.д.)
    code: str = Field(nullable=False, unique=True)
    
    # Название для отображения
    name: str = Field(nullable=False)
    
    # Описание
    description: Optional[str] = Field(default=None)
    
    # Категория (management, financial, legal, technical, safety, contact)
    category: str = Field(nullable=False)
    
    # Порядок отображения
    display_order: int = Field(default=0)
    
    # Активна ли роль
    is_active: bool = Field(default=True)
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    responsible_persons: List["ResponsiblePerson"] = Relationship(back_populates="role")
    
    class Config:
        from_attributes = True