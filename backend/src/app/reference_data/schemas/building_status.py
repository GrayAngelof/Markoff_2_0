# backend/src/app/reference_data/schemas/building_status.py
"""
Pydantic схема для BuildingStatus (справочник статусов зданий).
"""

from pydantic import ConfigDict
from .base import ReferenceSchema


class BuildingStatusSchema(ReferenceSchema):
    """Статус здания (полный ответ API)."""
    
    is_initial: bool | None = None
    allows_occupancy: bool | None = None

    model_config = ConfigDict(from_attributes=True)