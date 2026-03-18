# backend/src/models/dictionary/role_catalog.py
"""
Модель RoleCatalog для таблицы dictionary.role_catalog
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class RoleCatalog(SQLModel, table=True):
    """
    Модель роли
    """
    
    __tablename__ = "role_catalog"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(nullable=False, unique=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    category: str = Field(nullable=False)
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    class Config:
        from_attributes = True