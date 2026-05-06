# backend/src/app/reference_data/schemas/placement_status.py
"""
Pydantic схема для PlacementStatus (справочник статусов размещения).
"""

from pydantic import ConfigDict
from .base import ReferenceSchema


class PlacementStatusSchema(ReferenceSchema):
    """Статус размещения (полный ответ API)."""
    
    is_initial: bool | None = None

    model_config = ConfigDict(from_attributes=True)