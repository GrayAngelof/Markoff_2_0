# backend/src/app/reference_data/schemas/counterparty_type.py
"""
Pydantic схема для CounterpartyType (справочник типов контрагентов).
"""

from pydantic import ConfigDict
from .base import ReferenceSchema


class CounterpartyTypeSchema(ReferenceSchema):
    """Тип контрагента (полный ответ API)."""
    
    is_active: bool | None = None

    model_config = ConfigDict(from_attributes=True)