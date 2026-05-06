# backend/src/app/reference_data/schemas/base.py
"""
Базовая Pydantic-схема для всех справочников (reference data).
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReferenceSchema(BaseModel):
    """
    Общая схема для всех reference data сущностей.
    
    Содержит поля, которые есть у КАЖДОГО справочника в БД.
    """
    id: int
    code: str
    name: str
    description: str | None = None
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)