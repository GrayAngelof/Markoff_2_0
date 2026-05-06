# backend/src/app/reference_data/schemas/equipment_status.py
"""
Pydantic схема для EquipmentStatus (справочник статусов оборудования).
"""

from pydantic import ConfigDict
from .base import ReferenceSchema


class EquipmentStatusSchema(ReferenceSchema):
    """Статус оборудования (полный ответ API)."""
    
    is_initial: bool | None = None
    is_operational: bool | None = None

    model_config = ConfigDict(from_attributes=True)