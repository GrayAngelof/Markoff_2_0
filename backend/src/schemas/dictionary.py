# backend/src/schemas/dictionary.py
"""
Pydantic схемы для словарей и справочников.

Содержит схемы для статусов зданий и помещений.
"""

# ===== ИМПОРТЫ =====
from typing import Optional

from pydantic import BaseModel


# ===== СХЕМЫ =====
class BuildingStatusResponse(BaseModel):
    """Статус здания (ответ API)."""

    id: int
    code: str
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class RoomStatusResponse(BaseModel):
    """Статус помещения (ответ API)."""

    id: int
    code: str
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}