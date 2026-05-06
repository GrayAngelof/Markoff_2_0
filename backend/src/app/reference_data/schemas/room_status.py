# backend/src/app/reference_data/schemas/room_status.py
"""
Pydantic схема для RoomStatus (справочник статусов помещений).
"""

from pydantic import ConfigDict
from .base import ReferenceSchema


class RoomStatusSchema(ReferenceSchema):
    """Статус помещения (полный ответ API)."""
    
    is_initial: bool | None = None
    allows_rent: bool | None = None

    model_config = ConfigDict(from_attributes=True)