# backend/src/app/structure/models/complex.py
"""
Модель Complex для таблицы physical.complexes.
"""

from typing import Optional
from sqlmodel import Field
from .base import StructureBase


class Complex(StructureBase, table=True):
    """Комплекс зданий."""
    
    __tablename__: str = "complexes"  # type: ignore
    __table_args__ = {"schema": "physical"}
    
    name: str = Field(nullable=False, unique=True)
    address: Optional[str] = Field(default=None)
    owner_id: Optional[int] = Field(default=None)