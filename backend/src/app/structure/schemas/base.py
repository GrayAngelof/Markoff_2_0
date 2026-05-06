# backend/src/app/structure/schemas/base.py
"""
Базовые Pydantic схемы для физической иерархии (structure).
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class StructureTreeBase(BaseModel):
    """
    Базовая схема для дерева (минимальная информация).
    """
    id: int

    model_config = ConfigDict(from_attributes=True)


class StructureDetailBase(BaseModel):
    """
    Базовая схема для детальной информации.
    """
    id: int
    description: Optional[str] = None
    status_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)